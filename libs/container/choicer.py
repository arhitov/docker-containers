import os
import yaml
from helpers.str import str_to_bool
from helpers.parser_yml import ParserYml
from exceptions.container_unknown_type import ContainerUnknownTypeError
from libs.container.types.base import Config as BaseConfig
from libs.container.types.container import FILE_NAME as CONTAINER_FILE_NAME, Config as ContainerConfig
from libs.container.types.nested import FILE_NAME as NESTED_FILE_NAME, Config as NestedConfig
from libs.file_systems.directory import Directory
from libs.choicer_list import ChoicerList
from libs.i18n import trans
from exceptions.config_file_format_error import ConfigFileFormatError


def is_folder_container(folder: str) -> bool:
    return os.path.isdir(folder)


class Choicer:
    def __init__(self, folder: str):
        self.__folder = folder

    def choice(self):
        return self.__get_containers(self.__folder)

    def __get_containers(self, folder: str = None) -> list[ContainerConfig]:
        containers = []
        selected_list = self.__read_folder(self.__folder if folder is None else folder)
        for item in selected_list:
            if item.is_nested():
                print(trans('Block ":1" has internal divisions', item.name))
                containers = containers + self.__get_containers(item.directory.get_path())
            elif item.is_container():
                containers.append(item)
            else:
                raise ContainerUnknownTypeError(
                    trans(
                        'Unknown container type: ":1". Path: :2',
                        item.name,
                        item.directory.get_path(),
                    )
                )
        return containers

    @classmethod
    def __read_folder(cls, folder: str) -> list[BaseConfig]:
        # Указываем путь к каталогу, который хотим исследовать
        containers = []

        for directory in Directory(folder).get_subdirectories():
            if directory.file_exists(CONTAINER_FILE_NAME):
                file_name = CONTAINER_FILE_NAME
                class_name = ContainerConfig
            elif directory.file_exists(NESTED_FILE_NAME):
                file_name = NESTED_FILE_NAME
                class_name = NestedConfig
            else:
                continue

            file_path = directory.get_path(file_name)
            config = yaml.safe_load(directory.file_get_content(file_name))

            if not isinstance(config, dict) or 'name' not in config:
                raise ConfigFileFormatError(trans('Invalid configuration file format: :1', file_path))

            class_instance = class_name(config, directory)

            if class_instance.is_container():
                parser_yml = ParserYml(directory, 'docker-compose.yml')
                if parser_yml.has_file():
                    class_instance.set_docker_compose(parser_yml.load().validate(['services']).data())

            containers.append(class_instance)

        if len(containers) == 0:
            return []

        if Directory(folder).file_exists(NESTED_FILE_NAME):
            nested_config = yaml.safe_load(Directory(folder).file_get_content(NESTED_FILE_NAME))
            if not isinstance(nested_config, dict) or 'multi_choose' not in nested_config:
                raise ConfigFileFormatError(
                    trans(
                        'Invalid configuration file format: :1',
                        Directory(folder).get_path(NESTED_FILE_NAME)
                    )
                )
            multi_choose = str_to_bool(nested_config['multi_choose'])
        else:
            multi_choose = True

        choicer_list = ChoicerList([
                           {'name': container.name, 'container': container}
                           for container in containers
                       ])
        selected_items = choicer_list.choose_multi() if multi_choose else [choicer_list.choose_single()]
        selected_list = [selected['container'] for selected in selected_items]
        selected_names = [container.name for container in selected_list]
        # Выводим выбранные элементы
        print(trans('Your choices: ":1"', ' '.join(selected_names)))

        return selected_list
