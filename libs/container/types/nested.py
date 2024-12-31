from libs.container.types.base import Config as BaseConfig

FILE_NAME = 'nested.yml'


class Config(BaseConfig):
    def is_nested(self) -> bool:
        return True
