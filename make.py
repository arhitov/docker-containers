import os
import sys
import argparse
from helpers.console import text_error, text_success
from container_choicer import ContainerChoicer
from directory import Directory
from container import ContainerBuilder

FOLDER_CONTAINERS = 'containers'
FILE_CONFIG = 'example.yml'


def main(output_folder: str):
    output_directory = Directory(output_folder)
    if not output_directory.is_writable():
        print(text_error(
            f'Указанный каталог "{output_directory.get_path()}" не существует или не доступен на запись'
        ))
        sys.exit(1)

    # Выбираем доступные контейнеры
    containers = ContainerChoicer.choice_file(FOLDER_CONTAINERS)
    print(text_success(f'Вы выбрали контейнеры: {', '.join([container.name for container in containers])}"'))
    print()

    for container in containers:
        ContainerBuilder(container).make().write(
            output_directory
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Сборщик докер контейнеров')
    parser.add_argument(
        'output_folder',
        type=str,
        help=
        'Каталог куда будет сохранены файлы.'
        'Каталог должен быть доступен на запись.'
        'Относительный или полный путь.'
    )
    # parser.add_argument('-a', '--age', type=int, default=18, help='Возраст пользователя')
    args = parser.parse_args()

    try:
        main(args.output_folder)
    except Exception as e:
        error_message = e.args[0] if e.args else 'Unknown Error'
        print(text_error(error_message))

    sys.exit(0)
