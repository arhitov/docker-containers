import sys
import argparse
from helpers.console import text_error, text_success
from libs.i18n import Translation, trans
from libs.container.choicer import Choicer as ContainerChoicer
from libs.file_systems.directory import Directory
from libs.container.collector import Collector as ContainerCollector
from libs.question import ask_question

FOLDER_CONTAINERS = 'containers'
FOLDER_TRANSLATIONS = 'translations'
FILE_CONFIG = 'example.yml'

# Требуется версия 3.10 и выше для поддержки or в type hinting
# Требуется версия 3.7 и выше для поддержки сортировки ключей в dict
if sys.version_info < (3, 10):
    print('This script requires Python 3.10 or higher.')
    sys.exit(1)


def main(output_folder: str):
    # Выбираем доступные контейнеры
    containers = ContainerChoicer(FOLDER_CONTAINERS).choice()
    print(
        text_success(trans('You have selected containers: ', ', '.join([container.name for container in containers]))),
        end='\n\n'
    )

    (ContainerCollector(containers)
        .collect(Directory(FOLDER_CONTAINERS))
        .write(
            Directory(output_folder)
        ))


def check_output_folder(output_folder: str) -> None:
    directory = Directory(output_folder)
    if not directory.is_dir():
        if ask_question(trans('Create a catalog?')):
            directory.mkdir('', '0777')
        else:
            print(
                text_error(trans('The specified output directory does not exist'))
            )
            sys.exit(1)

    if not directory.is_empty_dir():
        print(
            text_error(trans('The specified output directory is not empty'))
        )
        sys.exit(1)

    if not directory.is_writable():
        print(
            text_error(trans('The specified output directory is not writable'))
        )
        sys.exit(1)


if __name__ == '__main__':

    # Устанавливаем каталог с переводами
    Translation.set_directory_translations(Directory(FOLDER_TRANSLATIONS))

    # Получаем аргуметы
    parser = argparse.ArgumentParser(description=trans('Docker container builder'))
    parser.add_argument(
        'output_folder',
        type=str,
        help=trans(
            'The directory where the files will be saved. The directory must be writable. Relative or full path.'
        )
    )
    # parser.add_argument('-a', '--age', type=int, default=18, help='Возраст пользователя')
    args = parser.parse_args()

    check_output_folder(args.output_folder)
    main(args.output_folder)

    # try:
    #     main(args.output_folder)
    # except Exception as e:
    #     error_message = e.args[0] if e.args else 'Unknown Error'
    #     print(text_error(error_message))

    sys.exit(0)
