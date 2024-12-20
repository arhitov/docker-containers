from typing import Union, List
from helpers.collection import Collection


class ChoicerList:
    def __init__(self, _list: Union[List[str], dict]):
        if Collection(_list).is_empty():
            raise ValueError('Список не должен быть пустым!')
        self.list = _list
        self._title = None
        self._name = None
        self._allow_empty = False

    def name(self, name: str):
        self._name = name
        return self

    def title(self, title: str):
        self._title = title
        return self

    def allow_empty(self):
        self._allow_empty = True
        return self

    def is_empty(self) -> bool:
        return len(self.list) == 0

    def choose_single(self):
        while True:
            try:
                allowed_list = []
                # Предлагаем пользователю выбрать
                print(self._get_exists_title())
                for idx, item in enumerate(self.list, start=1):
                    allowed_list.append(idx)
                    print(f'\t[{idx}]: {item}')
                # Преобразуем вводимые числа в целые значения
                choice_id_text = input(self._get_question_title())
                if choice_id_text == '':
                    if self._allow_empty:
                        return None
                    else:
                        print('Нужно что-то выбрать. Попробуйте снова.')
                        continue
                choice_id = int(choice_id_text)
                if choice_id not in allowed_list:
                    print(f'Недопустимый выбор: "{choice_id}". Попробуйте снова.')
                    continue
                else:
                    # Возвращаем выбранные элементы в список
                    if type(self.list) is list:
                        choice = self.list[choice_id - 1]
                    else:
                        choice = None
                        idx = 0
                        for key in self.list:
                            idx += 1
                            if idx == choice_id:
                                choice = self.list[key]
                                break
                    return choice
            except ValueError:
                print('Ошибка ввода. Используйте только цифры.')

    def choose_multi(self):
        while True:
            try:
                allowed_list = []
                # Предлагаем пользователю выбрать
                print(self._get_exists_title())
                for idx, item in enumerate(self.list, start=1):
                    allowed_list.append(item)
                    print(f'\t[{idx}]: {item}')
                # Преобразуем вводимые числа в целые значения
                choice_idx = list(map(int, input(self._get_question_title()).split()))
                if not choice_idx:
                    if self._allow_empty:
                        return [] if type(self.list) is list else {}
                    else:
                        print('Нужно что-то выбрать. Попробуйте снова.')
                        continue
                # Проверяем, что все введённые номера являются допустимыми индексами
                invalid_choices = [c for c in choice_idx if c > len(self.list) or c <= 0]
                if invalid_choices:
                    print(f'Недопустимый выбор: "{invalid_choices}". Попробуйте снова.')
                    continue
                else:
                    # Возвращаем выбранные элементы в список
                    # print(self.list, choice_idx)
                    if type(self.list) is list:
                        list_choices = [self.list[c - 1] for c in choice_idx]
                    else:
                        list_choices = {}
                        idx = 0
                        for key in self.list:
                            idx += 1
                            if idx in choice_idx:
                                list_choices[key] = self.list[key]
                    return list_choices
            except ValueError:
                print('Ошибка ввода. Используйте только цифры.')

    @staticmethod
    def _get_exists_title() -> str:
        return 'Доступный выбор: '

    def _get_choice_title(self) -> str:
        if self._title is not None:
            return self._title
        else:
            that = f' {self._name}' if self._name is not None else ''
            return f'Выберите номера{that} через пробел: '

    def _get_question_title(self) -> str:
        that = f' {self._name}' if self._name is not None else ''
        return f'Выберите номера{that} через пробел: '
