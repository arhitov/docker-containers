from typing import List
from helpers.collection import Collection
from libs.i18n import trans


class ChoicerList:
    def __init__(self, items: List[str] | List[dict] | dict):
        if Collection(items).is_empty():
            raise ValueError(trans('The list must not be empty!'))
        self.__items = items
        self.__title = None
        self.__name = None
        self.__allow_empty = False
        self.__allow_all = False

    def name(self, name: str) -> "ChoicerList":
        self.__name = name
        return self

    def title(self, title: str) -> "ChoicerList":
        self.__title = title
        return self

    def allow_empty(self) -> "ChoicerList":
        self.__allow_empty = True
        return self

    def allow_all(self) -> "ChoicerList":
        self.__allow_all = True
        return self

    def is_empty(self) -> bool:
        return len(self.__items) == 0

    @classmethod
    def __get_name_item(cls, item: dict | str) -> str:
        if isinstance(item, dict):
            return item['name']
        else:
            return item

    def choose_single(self):
        while True:
            try:
                allowed_list = []
                # Предлагаем пользователю выбрать
                print(self.__get_exists_title())
                for idx, item in enumerate(self.__items, start=1):
                    allowed_list.append(idx)
                    print(f'\t[{idx}]: {self.__get_name_item(item)}')
                # Преобразуем вводимые числа в целые значения
                choice_id_text = input(self.__get_question_title(True))
                if choice_id_text == '':
                    if self.__allow_empty:
                        return None
                    else:
                        print(trans('You need to select something. Try again.'))
                        continue
                choice_id = int(choice_id_text)
                if choice_id not in allowed_list:
                    print(trans('Invalid selection: ":1". Please try again.', choice_id))
                    continue
                else:
                    # Возвращаем выбранные элементы в список
                    if type(self.__items) is list:
                        choice = self.__items[choice_id - 1]
                    else:
                        choice = None
                        idx = 0
                        for key in self.__items:
                            idx += 1
                            if idx == choice_id:
                                choice = self.__items[key]
                                break
                    return choice
            except ValueError:
                print(trans('Input error. Use only numbers.'))

    def choose_multi(self):
        while True:
            try:
                allowed_list = []
                # Предлагаем пользователю выбрать
                print(self.__get_exists_title())
                idx_all = []
                for idx, item in enumerate(self.__items, start=1):
                    idx_all.append(str(idx))
                    allowed_list.append(item)
                    print(f'\t[{idx}]: {self.__get_name_item(item)}')
                # Преобразуем вводимые числа в целые значения
                choice_idx_text = input(self.__get_question_title(False))
                if choice_idx_text == '*' and self.__allow_all:
                    choice_idx_text = ' '.join(idx_all)
                choice_idx = list(map(int, choice_idx_text.split()))
                if not choice_idx:
                    if self.__allow_empty:
                        return [] if type(self.__items) is list else {}
                    else:
                        print(trans('You need to select something. Try again.'))
                        continue
                # Проверяем, что все введённые номера являются допустимыми индексами
                invalid_choices = [c for c in choice_idx if c > len(self.__items) or c <= 0]
                if invalid_choices:
                    print(trans('Invalid selection: ":1". Please try again.', invalid_choices))
                    continue
                else:
                    # Возвращаем выбранные элементы в список
                    # print(self.__items, choice_idx)
                    if type(self.__items) is list:
                        list_choices = [self.__items[c - 1] for c in choice_idx]
                    else:
                        list_choices = {}
                        idx = 0
                        for key in self.__items:
                            idx += 1
                            if idx in choice_idx:
                                list_choices[key] = self.__items[key]
                    return list_choices
            except ValueError:
                print(trans('Input error. Use only numbers.'))

    @staticmethod
    def __get_exists_title() -> str:
        return trans('Available choice: ')

    def __get_question_title(self, single: bool = False) -> str:
        string = ''
        if self.__title is not None:
            string += self.__title
        else:
            that = f' {self.__name}' if self.__name is not None else ''
            string += \
                trans('Select number :1', that) \
                if single else \
                trans('Select numbers :1 separated by space', that)
        if self.__allow_all:
            string += f' [{trans('enter * to select all')}]'
        elif self.__allow_empty:
            string += f' [{trans('press Enter to skip')}]'
        return string + ': '
