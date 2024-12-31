import datetime
from libs.i18n import trans


def merge_dicts(d1, d2):
    """
    Рекурсивная функция для слияния двух многомерных словарей.

    :param d1: Первый словарь
    :param d2: Второй словарь
    :return: Слияние двух словарей
    """
    result = d1.copy()
    for key in d2:
        if key in result and isinstance(result[key], dict) and isinstance(d2[key], dict):
            # Если значение является словарем, то вызываем функцию рекурсивно
            result[key] = merge_dicts(result[key], d2[key])
        elif key in result and isinstance(result[key], list) and isinstance(d2[key], list):
            result[key].extend(d2[key])
        else:
            # Иначе просто обновляем значение
            result[key] = d2[key]
    return result


def process_named_dict(data: dict[str, any] | list[dict]) -> dict[str, any]:
    if isinstance(data, dict):
        return data

    result = {}
    for item in data:
        key = item.get('name')
        result[key] = item

    return result


TYPE_MAP = {
    'int': int,
    'float': float,
    'bool': bool,
    'str': str,
    'list': list,
    'dict': dict,
    'datetime': datetime.datetime
}


class RuleValidator(object):
    def __init__(self, rule: str):
        parts = rule.split(':')
        self.__key = parts[0].strip()
        self.__type = parts[1].strip().lower()
        self.__nullable = False

        # Проверим, есть ли указание на nullable
        if self.__type.endswith('?'):
            self.__nullable = True
            self.__type = self.__type.rstrip('?')

    @property
    def key(self) -> str:
        return self.__key

    @property
    def type(self) -> str:
        return self.__type

    @property
    def nullable(self) -> bool:
        return self.__nullable

    def get_nested(self) -> list[str]:
        return self.key.split('.')

    def is_nested(self) -> bool:
        return len(self.get_nested()) > 1


class DictValidator:
    def __init__(self, data: dict, rules: list):
        self.__data = data
        self.__rules = self.__prepare_rules(rules)
        self.__errors = []

    @staticmethod
    def __prepare_rules(rules) -> dict:
        result = {}
        for rule_str in rules:
            rule = RuleValidator(rule_str)
            if not rule.is_nested():
                result[rule.key] = {'_rule': rule, 'nested': {}}
                continue

            current_level = result
            rule_level = {}
            key_nested = rule.get_nested()
            # Переходим на нужный уровень
            while key_nested:
                key_part = key_nested.pop(0)
                if key_part not in current_level:
                    current_level[key_part] = {'_rule': None, 'nested': {}}
                rule_level = current_level[key_part]
                current_level = current_level[key_part]['nested']
            rule_level['_rule'] = rule

        return result

    @classmethod
    def __check_key(cls, key: str, data: dict) -> dict:
        if not isinstance(data, dict) or key not in data:
            return {
                'status': False,
            }
        return {
            'status': True,
            'value': data[key],
        }

    @classmethod
    def __check_value_type(cls, value, value_type) -> bool:
        """Проверка типа данных"""
        return isinstance(value, value_type)

    def __validate_rule(self, key: str, rule: RuleValidator, nested: dict, data: dict) -> None:
        # Проверка структуры
        check = self.__check_key(key, data)
        if check['status'] is True:
            value_type = TYPE_MAP.get(rule.type)
            if not value_type:
                self.__errors.append(trans('Data type ":1" is not supported.', rule.type))
                return
            if not self.__check_value_type(check['value'], value_type):
                self.__errors.append(
                    trans(
                        'Key ":1" has invalid data type. Expected ":2", got ":3".',
                        rule.key,
                        rule.type,
                        type(check['value']).__name__,
                    )
                )
            if {} != nested:
                for n_key, n_rule in nested.items():
                    self.__validate_rule(n_key, n_rule['_rule'], n_rule['nested'], check['value'])
            return
        elif rule.nullable is True:
            return
        else:
            self.__errors.append(trans('Key ":1" does not exist', rule.key))
            return


        # Получение типа данных



    def is_valid(self) -> bool:
        """Проверка всех правил и возврат результата."""
        for key, rule in self.__rules.items():
            self.__validate_rule(key, rule['_rule'], rule['nested'], self.__data)
        return len(self.__errors) == 0

    def get_errors(self) -> list:
        """Возврат списка сообщений об ошибках."""
        return self.__errors
