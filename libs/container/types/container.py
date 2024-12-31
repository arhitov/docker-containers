from libs.container.types.base import Config as BaseConfig

FILE_NAME = 'container.yml'


class Config(BaseConfig):
    def is_container(self) -> bool:
        return True
