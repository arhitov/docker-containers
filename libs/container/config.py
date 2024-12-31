class Config:
    def __init__(self, options: dict):
        self.__options = options

    def get(self, key: str = None, default=None):
        return self.__options if key is None else self.__options.get(key, default)

    def has(self, key: str):
        return key in self.__options
