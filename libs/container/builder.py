import sys
from libs.file_systems.directory import Directory
from helpers.console import execute_command, Command, text_error
from helpers.dict import merge_dicts, DictValidator
from libs.yml.builder_yml import BuilderYml
from pkg_resources import parse_version
from data.env.env_variable import EnvVariable
from libs.i18n import trans


class Builder(object):
    def __init__(self,
                 config_env: list[EnvVariable],
                 config_docker_compose: dict,
                 containers_folders: list,
                 containers_files: list,
                 ):
        self.__config_env = config_env
        self.__config_docker_compose = config_docker_compose
        self.__containers_folders = containers_folders
        self.__containers_files = containers_files

    def build_env(self) -> str:
        groups = {'': []}

        # Распределение по группам
        for variable in self.__config_env:
            group = '' if variable.group is None else variable.group
            if group not in groups:
                groups[group] = []
            groups[group].append(variable)

        # Сборка файла
        result = ''
        for group, items in groups.items():
            if not items:
                continue
            result += f'# {group}\n'
            for variable in items:
                result += f'{variable.name}={variable.value}\n'
            result += '\n'
        return result

    def build_docker_compose(self) -> str:
        docker_compose = self.__config_docker_compose
        docker_compose_sorted = {}

        if 'version' in docker_compose:
            docker_compose_version = execute_command(r"docker compose version | grep -oP '(?<=version )\S+' | head -1")
            # Начиная с версии v2.4, Docker Compose перестал требовать явного указания версии (version) в файле
            # docker-compose.yml. Теперь версия Docker Compose определяется автоматически на основе синтаксиса и
            # возможностей, используемых в файле конфигурации.
            if parse_version('v2.4'.lstrip('v')) > parse_version(docker_compose_version.lstrip('v')):
                docker_compose_sorted['version'] = docker_compose['version']
            del docker_compose['version']
        if 'services' in docker_compose:
            docker_compose_sorted['services'] = docker_compose['services']
            del docker_compose['services']
        if 'volumes' in docker_compose:
            docker_compose_sorted['volumes'] = docker_compose['volumes']
            del docker_compose['volumes']
        if 'networks' in docker_compose:
            docker_compose_sorted['networks'] = docker_compose['networks']
            del docker_compose['networks']

        return BuilderYml(merge_dicts(
            docker_compose_sorted,
            docker_compose,
        )).to_string()

    @classmethod
    def check_files(cls, files: list[dict]) -> None:
        for files_data in files:
            for file in files_data['list']:
                cls.check_file(files_data['directory'], file)

    @classmethod
    def check_folders(cls, folders: list[dict]) -> None:
        for folders_data in folders:
            cls.check_folder(folders_data)

    @staticmethod
    def check_folder(folder: dict) -> None:
        validator = DictValidator(
            folder,
            [
                'patch:str',
                'chmod:dict?',
                'chmod.mode:str',
                'chmod.owner:str?',
                'chmod.group:str?',
            ],
        )
        if not validator.is_valid():
            raise ValueError(
                trans(
                    'Directory configuration ":1" is not valid. Errors: :2',
                    folder,
                    ', '.join(validator.get_errors()),
                )
            )

    @staticmethod
    def check_file(directory: Directory, file: dict) -> None:
        if 'file' not in file:
            raise FileNotFoundError(
                trans(
                    'Configuration file ":1" does not contain ":2". Directory: :3',
                    file,
                    'file',
                    directory.get_path(),
                )
            )
        if 'content' not in file:
            directory_file = directory.join_path(file['folder']) if 'folder' in file else directory
            if not directory_file.file_exists(file['file']):
                raise FileNotFoundError(
                    trans(
                        'Configuration file ":1" does not contain "content" or file is missing. File: :2',
                        file,
                        directory_file.get_path(file['file']),
                    )
                )

    def write(self, directory: Directory):
        """Выполняет запись собранных данных в указанный каталог. Каталог должен быть пусто и доступен на запись.

        :param directory: Класс работы с каталогом с указанным каталогом куда нужно произвести запись.
        :type directory: Directory
        """

        # Собираем контент файла .env
        env_content = self.build_env()
        # Собираем контент файла docker-compose.yml
        docker_compose_content = self.build_docker_compose()
        # Проверяем каталоги
        self.check_folders(self.__containers_folders)
        # Проверяем файлы
        self.check_files(self.__containers_files)

        # Сохраняем файлы
        directory.file_put_content(
            '.env',
            env_content,
        )
        directory.file_put_content(
            'docker-compose.yml',
            docker_compose_content,
        )
        # Создаём каталоги
        self.__create_folders(directory, self.__containers_folders)
        
        # Копируем файлы
        self.__copy_files(directory, self.__containers_files)

        # Проверяем валидация собранного файла docker-compose.yml
        command = Command(f'docker compose -f {directory.get_path('docker-compose.yml')} config --quiet',
                          stderr=sys.stderr).run()
        if 0 != command.get_code():
            print(text_error(
                trans(
                    'File ":1" contains critical errors',
                    directory.get_path('docker-compose.yml'),
                )
            ))
            sys.exit(1)

    @staticmethod
    def __create_folders(directory: Directory, folders: list[dict]) -> None:
        for folder in folders:
            chmod = folder['chmod'] if 'chmod' in folder else {}
            directory.mkdir(folder['patch'], **chmod)

    @staticmethod
    def __copy_files(directory: Directory, files: list[dict]) -> None:
        for files_data in files:
            for file in files_data['list']:
                # Куда копировать
                directory_to = directory.join_path(file['to']) if 'to' in file else directory
                if 'content' in file:
                    content = file['content']
                elif 'folder' in file:
                    content = files_data['directory'].join_path(file['folder']).file_get_content(file['file'])
                else:
                    content = files_data['directory'].file_get_content(file['file'])
                directory_to.file_put_content(file['file'], content)

