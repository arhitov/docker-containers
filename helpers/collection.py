from typing import Union, List


class Collection:
    def __init__(self, _list: Union[List[str], dict]):
        self._list = _list

    def is_empty(self) -> bool:
        if isinstance(self._list, list):
            return self._list == []
        elif isinstance(self._list, dict):
            return self._list == {}
