from libs.file_systems.directory import Directory
from libs.container.types.base import Config as ContainerConfig
from libs.container.builder import Builder as ContainerBuilder
from libs.choicer_list import ChoicerList
from helpers.parser_yml import ParserYml
from helpers.dict import merge_dicts, process_named_dict
from data.env.env_variable import EnvVariable
from libs.i18n import trans


def _process_config_env(config: dict) -> list[EnvVariable]:
    """Если в конфигурации есть перечисления вариантов, даём выбрать
    :param config: Конфигурация в виде словаря
    :type config: dict
    :return: Нормализованная конфигурация
    :rtype: dict
    """
    result = []
    for key, data in config.items():
        default = data['default'] if 'default' in data else None
        choice = None
        if 'enums' in data:
            print(trans('Variable ":1"', key))
            if default is not None:
                print(trans('Default value is ":1"', default))
            choicer = ChoicerList(data['enums']).name(trans('meanings'))
            if default is not None:
                choicer.allow_empty()
            choice = choicer.choose_single()
            if choice is None:
                choice = default
            config[key]['value'] = choice
        variable = EnvVariable(
            data['name'] if 'name' in data else key,
            choice if choice is not None else default,
        )
        if 'group' in data:
            variable.set_group(data['group'])
        if 'default' in data:
            variable.set_default(data['default'])
        result.append(variable)
    return result


class Collector:
    """Класс собирающий информацию о контейнерах
    :param containers: Список контейнеров
    :type containers: list[ContainerConfig]
    """

    def __init__(self, containers: list[ContainerConfig]):
        self.__containers = containers

    def collect(self, root_directory: Directory) -> "ContainerBuilder":
        base_config = (ParserYml(root_directory, 'base-container.yml')
                       .load()
                       .validate(['env'])
                       .data())
        base_docker_compose = (ParserYml(root_directory, 'base-docker-compose.yml')
                               .load()
                               .validate(['version', 'networks'])
                               .data())

        containers_env = {}
        containers_docker_compose = {}
        containers_folders = []
        containers_files = []

        for container in self.__containers:
            data = self.__process_container(container)
            # Объединяем env конфиги
            containers_env = merge_dicts(
                containers_env,
                process_named_dict(container.config.get('env', {})),
            )
            # Объединяем docker_compose
            containers_docker_compose = merge_dicts(
                containers_docker_compose,
                data['docker_compose'],
            )
            # Собираем информацию о каталогах
            if container.config.has('folders'):
                containers_folders.extend(container.config.get('folders'))
            # Собираем информацию о файлах
            if container.config.has('files'):
                files = container.config.get('files')
                if data['dockerfile_content'] is not None:
                    for file in files:
                        if 'Dockerfile' == file['file']:
                            file['content'] = data['dockerfile_content']
                containers_files.append({
                    'directory': container.directory,
                    'list': files
                })

        return ContainerBuilder(
            # Объединяем env конфиги контейнеров и глобальный
            _process_config_env(merge_dicts(
                process_named_dict(base_config.get('env', {})),
                containers_env,
            )),
            # Объединяем docker_compose контейнеров и глобальный
            merge_dicts(
                base_docker_compose,
                containers_docker_compose,
            ),
            containers_folders,
            containers_files,
        )

    @staticmethod
    def __process_container(container: ContainerConfig) -> dict:
        # Если есть предложение выбора, даём пользователю выбрать.
        choosing_data = container.config.get('choose')
        if choosing_data is not None:
            # Запрашиваем ввод у пользователя
            print(trans('Container ":1"', container.name))
            choosing_list = (
                choosing_data['list']
                if isinstance(choosing_data['list'], list) else
                [item for item in choosing_data['list'].values()]
            )
            config = container.config.get()
            choose_config = ChoicerList(choosing_list).title(choosing_data['question']).choose_single()
            if 'folder' not in choose_config:
                choose_config['folder'] = choose_config['name']
            # Проверяем есть ли файлы в выборе, если есть проверяем наличие folder и если нет, то дописываем
            if 'files' in choose_config:
                for file in choose_config['files']:
                    # Если нет, то дописываем
                    file['folder'] = choose_config['folder'] if 'folder' not in file else file['folder']

            # Сливаем выбор с конфигом контейнера
            del config['choose']
            config = merge_dicts(
                config,
                choose_config,
            )
            is_choose = True
        else:
            config = container.config.get()
            if 'folder' not in config:
                config['folder'] = None
            is_choose = False

        if 'folder' not in config:
            raise ValueError(trans(
                'Key "folder" is not defined for :1. Please correct the configuration file.',
                config['name']
            ))
        if 'dockerfile' not in config:
            config['dockerfile'] = True

        # Получаем доступных надстроек
        extensions = config.get('extensions', {})
        # Если список расширений является списком, приводим его к виду словаря
        if isinstance(extensions, list):
            extensions = {key: {'name': key} for key in extensions}
        # Если нет каталога для глобального расширения, то добавляем каталог в глобальном пространстве
        for key, data in extensions.items():
            if 'folder' not in data:
                extensions[key]['folder'] = '../extensions/' + key

        # Дополняем расширения из выбора, если был сделан выбор
        if is_choose:
            choice_extensions = config.get('extensions', {})
            choice_extensions = {} if choice_extensions is None else choice_extensions
            # Если список расширений является списком, приводим его к виду словаря
            if isinstance(choice_extensions, list):
                choice_extensions = {key: {'name': key} for key in choice_extensions}
            # Если нет каталога для индивидуального расширения, то добавляем каталог в пространстве выбора
            for key, data in choice_extensions.items():
                if 'folder' not in data:
                    choice_extensions[key]['folder'] = config.get('folder') + '/extensions/' + key
            extensions.update(choice_extensions)

        # Если список расширений не пуст, предлагаем пользователю выбрать
        dockerfile_content_extensions = {}
        if {} != extensions:
            del config['extensions']
            # Нормализуем список расширений, добавляя недостающие элементы
            for element in extensions:
                if 'name' not in extensions[element]:
                    extensions[element]['name'] = element

            choice_extensions = ChoicerList(extensions).name(trans('extensions')).allow_empty().allow_all().choose_multi()

            # Собираем Dockerfile для расширения
            choice_extensions_sting = ', '.join(
                [choice_extension['name'] for choice_extension in choice_extensions.values()])
            print(trans('You have selected extensions: :1', choice_extensions_sting))
            for ext_key, ext_data in choice_extensions.items():
                ext_directory = Directory(container.directory.get_path()).join_path(ext_data.get(
                    'folder',
                    config['folder'] + '/extensions/' + ext_key
                ))
                if config['dockerfile']:
                    if not ext_directory.file_exists('Dockerfile.stub'):
                        raise FileNotFoundError(
                            trans(
                                'There is no "Dockerfile.stub" for extension ":1/:2". :3',
                                config['name'],
                                ext_key,
                                ext_directory.get_path(),
                            )
                        )

                    dockerfile_content_extensions[ext_key] = ext_directory.file_get_content('Dockerfile.stub')

        dockerfile_content = None
        if config['dockerfile']:
            # Собираем глобальный Dockerfile
            dockerfile_directory = Directory(container.directory.get_path())
            if config['folder'] is not None:
                dockerfile_directory = dockerfile_directory.join_path(config['folder'])
            dockerfile_content = dockerfile_directory.file_get_content('Dockerfile.stub')
            dockerfile_content = (
                dockerfile_content.replace('{extensions}', "\n\n".join(dockerfile_content_extensions.values()))
                if dockerfile_content_extensions else
                dockerfile_content.replace('{extensions}', '# Not selected')
            )

        return {
            'config': config,
            'docker_compose': (ParserYml(container.directory, 'docker-compose.yml')
                               .load()
                               .validate(['services'])
                               .data()),
            'dockerfile_content': dockerfile_content,
        }
