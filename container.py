import os

from config import ConfigData
from directory import Directory
from helpers.choicer_list import ChoicerList

CONTAINER_FILE = 'container.yml'


class ContainerData(object):
    def __init__(self, name: str, folder: str):
        self.name = name
        self.folder = folder

    def get_file(self) -> str:
        return os.path.join(self.folder, CONTAINER_FILE)


class MakeData(object):
    def __init__(self, dockerfile_content: str):
        self.dockerfile_content = dockerfile_content


class ContainerBuilder:
    def __init__(self, container_data: ContainerData):
        self.folder = container_data.folder
        self.config = ConfigData(container_data.get_file())
        self.name = self.config.get('name', '~')
        self.makeData = None

    def make(self):
        # Если есть предложение выбора, даём пользователю выбрать.
        choosing_data = self.config.get('choose')
        is_choose = False
        if choosing_data is not None:
            # Запрашиваем ввод у пользователя
            print(f'Контейнер "{self.name}"')
            selected_item = ChoicerList(choosing_data['list']).title(choosing_data['question']).choose_single()
            chosen = self.config.get(choosing_data['key'])
            config = chosen[selected_item]
            if config is None:
                config = {}
            if 'name' not in config:
                config['name'] = self.name + '-' + selected_item
            is_choose = True
        else:
            config = self.config.get()

        if 'folder' not in config:
            raise ValueError(f'Для {config['name']} не определён "folder". Поправьте конфигурационный файл')

        # Получаем доступных надстроек
        extensions = self.config.get('extensions', {})
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
        if bool(extensions):
            # Нормализуем список расширений, добавляя недостающие элементы
            for element in extensions:
                if 'name' not in extensions[element]:
                    extensions[element]['name'] = element

            choice_extensions = ChoicerList(extensions).name('расширения').allow_empty().choose_multi()

            # Собираем Dockerfile для расширения
            choice_extensions_sting = ', '.join(
                [choice_extension['name'] for choice_extension in choice_extensions.values()])
            print(f'Вы выбрали расширения: {choice_extensions_sting}.')
            for ext_key, ext_data in choice_extensions.items():
                ext_directory = Directory(self.folder).join_path(ext_data.get(
                   'folder',
                   config['folder'] + '/extensions/' + ext_key
                ))
                if not ext_directory.file_exists('Dockerfile.stub'):
                    raise FileNotFoundError(
                        f'Для расширения "{config['name']}/{ext_key}" отсутствует "Dockerfile.stub". {ext_directory.get_path()}'
                    )
                dockerfile_content_extensions[ext_key] = ext_directory.file_get_content('Dockerfile.stub')

        # Собираем глобальный Dockerfile
        dockerfile_content = Directory(self.folder).join_path(config['folder']).file_get_content('Dockerfile.stub')
        dockerfile_content.replace('{extensions}', "\n\n".join(dockerfile_content_extensions.values()))

        self.makeData = MakeData(
            dockerfile_content
        )

        return self

    def write(self, directory: Directory):
        """Выполняет запись собранных данных в указанный каталог. Каталог должен быть пусто и доступен на запись.

        :param directory: Класс работы с каталогом с указанным каталогом куда нужно произвести запись.
        :type directory: Directory
        """
        if self.makeData is None:
            raise RuntimeError('Не была выполнена сборка. Выполните метод "make".')
        return self.config.get('name')
