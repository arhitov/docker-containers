import yaml


class BuilderYml:
    def __init__(self, data: dict):
        self.__data = data

    def to_string(self) -> str:
        return yaml.dump(self.__data, sort_keys=False, default_flow_style=False, width=300)
