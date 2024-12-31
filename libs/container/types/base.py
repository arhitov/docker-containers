from libs.file_systems.directory import Directory
from libs.container.config import Config as ContainerConfig
from exceptions.was_already_determined import WasAlreadyDetermined
from libs.i18n import trans


class Config:
    def __init__(self, options: dict, directory: Directory):
        self.__options = options
        self.__config = None
        self.__directory = directory
        self.__setting = {}
        self.__docker_compose = None

    def is_nested(self) -> bool:
        return False

    def is_container(self) -> bool:
        return False

    @property
    def directory(self) -> Directory:
        return self.__directory

    @property
    def name(self) -> str:
        return self.__options['name']

    def options(self) -> dict:
        return self.__options

    @property
    def config(self) -> ContainerConfig:
        if self.__config is None:
            self.__config = ContainerConfig(self.__options)
        return self.__config

    def set_setting(self, key: str, value) -> "Config":
        self.__setting[key] = value
        return self

    def get_setting(self, key: str):
        return self.__setting[key] if key in self.__setting else None

    def has_docker_compose(self) -> bool:
        return self.__docker_compose is not None

    def get_docker_compose(self) -> dict:
        return self.__docker_compose

    def set_docker_compose(self, value: dict) -> "Config":
        if self.__docker_compose is not None:
            raise WasAlreadyDetermined(trans('Property "docker_compose" cannot be overridden'))
        self.__docker_compose = value
        return self
