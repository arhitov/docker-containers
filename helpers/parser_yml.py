import yaml
from libs.file_systems.directory import Directory
from exceptions.config_file_format_error import ConfigFileFormatError
from libs.i18n import trans


class ParserYml:
    def __init__(self, directory: Directory, file_name: str):
        self.__directory = directory
        self.__file_name = file_name
        self.__data = {}

    def has_file(self) -> bool:
        return self.__directory.file_exists(self.__file_name)

    def load(self) -> 'ParserYml':
        data = yaml.safe_load(self.__directory.file_get_content(self.__file_name))
        if not isinstance(data, dict):
            raise ConfigFileFormatError(
                trans(
                    'Invalid file format: ":1". Path: :2',
                    self.__file_name,
                    self.__directory.get_path(self.__file_name),
                )
            )
        self.__data = data
        return self

    def validate(self, keys: list) -> 'ParserYml':
        for key in keys:
            if key not in self.__data:
                raise ConfigFileFormatError(
                    trans(
                        'Key ":1" is missing in file: ":2". Path: :3',
                        key,
                        self.__file_name,
                        self.__directory.get_path(self.__file_name),
                    )
                )
        return self

    def data(self) -> dict:
        return self.__data
