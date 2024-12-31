class EnvVariable(object):
    def __init__(self, name: str, value: any):
        self.__name = name
        self.__value = value
        self.__group = None
        self.__default = None

    def set_group(self, name: str) -> 'EnvVariable':
        self.__group = name
        return self

    def set_default(self, name: str) -> 'EnvVariable':
        self.__default = name
        return self

    @property
    def name(self) -> str:
        return self.__name

    @property
    def group(self) -> str:
        return self.__group

    @property
    def value(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'EnvVariable(name={self.__name}, value={self.__value}, group={self.__group}, default={self.__default})'
