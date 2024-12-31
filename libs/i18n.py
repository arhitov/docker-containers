import locale
import json
from typing import Type
from libs.file_systems.directory import Directory


def trans(string: str, *args) -> str:
    return Translation.trans(string, *args)


class Translation:
    # Example: ru_RU
    __locale_lang = None
    __translation_dir = None
    __translations = None

    @classmethod
    def set_directory_translations(cls, directory: Directory) -> Type['Translation']:
        cls.__translation_dir = directory
        return cls

    @classmethod
    def set_locale_lang(cls, lang: str) -> Type['Translation']:
        """Установка языка
        :param lang: Example: ru_RU
        """
        cls.__locale_lang = lang
        return cls

    @classmethod
    def get_locale_lang(cls) -> str:
        return cls.__locale_lang if cls.__locale_lang is not None else locale.getlocale()[0]

    @classmethod
    def trans(cls, string, *args) -> str:
        cls.load_translations()
        if (cls.__translations is not None) and string in cls.__translations:
            string = cls.__translations[string]
        for idx, value in enumerate(args, start=1):
            string = string.replace(f':{idx}', str(value))
        return string

    @classmethod
    def load_translations(cls) -> None:
        if (cls.__translations is None) and cls.__translation_dir.file_exists(f'{cls.get_locale_lang()}.json'):
            cls.__translations = json.loads(cls.__translation_dir.file_get_content(f'{cls.get_locale_lang()}.json'))
