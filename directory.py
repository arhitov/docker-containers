import os
import tempfile
from typing import List


class Directory:
    def __init__(self, path: str):
        self.directory = os.path.abspath(path)
        
    def join_path(self, path: str):
        return Directory(self.get_path(path))

    def get_path(self, path: str = None) -> str:
        if path is not None:
            return os.path.abspath(os.path.join(self.directory, path))
        else:
            return self.directory

    def is_dir(self, path: str = None) -> bool:
        return os.path.isdir(self.get_path(path))

    def is_dir_or_fail(self, path: str = None):
        if not self.is_dir(path):
            raise ValueError(f'Указанный путь "{self.get_path(path)}" не является каталогом.')

    def is_writable(self, path: str = None) -> bool:
        if not os.path.isdir(self.get_path(path)):
            return False
        try:
            temp_file = tempfile.TemporaryFile(dir=self.get_path(path))
            temp_file.close()
            return True
        except OSError:
            return False

    def get_subdirectories(self) -> List[str]:
        self.is_dir_or_fail()
        dirs = [
            directory for directory in os.listdir(self.directory)
            if os.path.isdir(os.path.join(self.directory, directory))
        ]
        return dirs

    def file_get_content(self, filename: str) -> str:
        self.is_dir_or_fail()
        with open(os.path.join(self.directory, filename), 'r') as file:
            # Читаем всё содержимое файла
            content = file.read()
        return content

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
