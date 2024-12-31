import os
import pwd
import grp
import tempfile
from typing import List
# from libs.i18n import trans


class Directory:
    def __init__(self, path: str):
        self.__directory = os.path.abspath(path)
        
    def join_path(self, path: str):
        return Directory(self.get_path(path))

    def get_path(self, path: str = None) -> str:
        if path is not None:
            return os.path.abspath(os.path.join(self.__directory, path))
        else:
            return self.__directory

    def file_get_content(self, filename: str) -> str:
        self.is_dir_or_fail()
        with open(os.path.join(self.__directory, filename), 'r') as file:
            # Читаем всё содержимое файла
            content = file.read()
        return content

    def file_put_content(self, filename: str, content: str) -> None:
        self.mkdir()
        with open(os.path.join(self.__directory, filename), 'w') as file:
            file.write(content)

    def file_exists(self, file: str, folder: str = None) -> bool:
        full_folder = self.get_path(folder)
        # print(self.directory, full_folder)

        if not os.path.exists(full_folder):
            # raise FileNotFoundError(f'Каталог "{self.directory}" отсутствует.')
            # print(f'Каталог "{full_folder}" отсутствует.')
            return False

        if not os.path.isfile(f'{full_folder}/{file}'):
            # raise FileNotFoundError(f'Файл "{file}" не найден в каталоге "{self.directory}".")
            # print(f'Файл "{file}" не найден в каталоге "{full_folder}".')
            return False

        # print(f'Файл "{file}" найден в каталоге "{full_folder}".')
        return True

    def is_dir(self, path: str = None) -> bool:
        return os.path.isdir(self.get_path(path))

    def is_dir_or_fail(self, path: str = None):
        if not self.is_dir(path):
            raise ValueError(f'The specified path "{self.get_path(path)}" is not a directory.')
            # @TODO ImportError: cannot import name 'trans' from partially initialized module 'libs.i18n' (most likely due to a circular import)
            # raise ValueError(trans('The specified path ":1" is not a directory.', self.get_path(path)))

    def is_writable(self, path: str = None) -> bool:
        if not os.path.isdir(self.get_path(path)):
            return False
        try:
            temp_file = tempfile.TemporaryFile(dir=self.get_path(path))
            temp_file.close()
            return True
        except OSError:
            return False

    def get_subdirectories(self) -> List["Directory"]:
        self.is_dir_or_fail()
        dirs = [
            self.join_path(directory) for directory in os.listdir(self.__directory)
            if os.path.isdir(os.path.join(self.__directory, directory))
        ]
        return dirs

    def is_empty_dir(self, path: str = None) -> bool:
        # Получаем содержимое каталога
        contents = os.listdir(self.get_path(path))
        return len(contents) == 0

    def mkdir(self, path: str = None, mode: str = '0777', owner: str = None, group: str = None):
        self.__mkdir(self.get_path(path), mode, owner, group)

    @classmethod
    def __mkdir(cls, path: str, mode: str, owner: str = None, group: str = None):
        if os.path.exists(path):
            return

        parent_dir = os.path.dirname(path)
        # Если это не корневой каталог
        if parent_dir != path:
            # Рекурсивно создаем родительские директории
            cls.__mkdir(parent_dir, mode, owner, group)

        os.mkdir(path, mode=int(mode, 8))
        # Устанавливаем необходимые права доступа
        os.chmod(path, mode=int(mode, 8))

        # Установка владельца и группы для созданного каталога
        if owner is not None:
            os.chown(
                path,
                pwd.getpwnam(owner).pw_uid,
                grp.getgrnam(group).gr_gid if group is not None else pwd.getpwnam(owner).pw_gid,
            )
