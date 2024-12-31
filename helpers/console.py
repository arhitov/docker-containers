import subprocess
import re
import sys

# Цвет текста
COLOR_TEXT_BLACK = 30  # Черный
COLOR_TEXT_RED = 31  # Красный
COLOR_TEXT_GREEN = 32  # Зеленый
COLOR_TEXT_YELLOW = 33  # Желтый
COLOR_TEXT_BLUE = 34  # Синий
COLOR_TEXT_PURPLE = 35  # Пурпурный
COLOR_TEXT_CYAN = 36  # Голубой
COLOR_TEXT_WHITE = 37  # Белый
# Цвет фона
COLOR_BG_BLACK = 40  # Черный
COLOR_BG_RED = 41  # Красный
COLOR_BG_GREEN = 42  # Зеленый
COLOR_BG_YELLOW = 43  # Желтый
COLOR_BG_BLUE = 44  # Синий
COLOR_BG_PURPLE = 45  # Пурпурный
COLOR_BG_CYAN = 46  # Голубой
COLOR_BG_WHITE = 47  # Белый
# Стиль
TEXT_BOLD = 1  # Жирный
TEXT_SEMIBOLD = 2  # Полужирный
TEXT_UNDERLINED = 4  # Подчеркнутый
TEXT_STRIKETHROUGH = 9  # Перечеркнутый


# Определение функций для удобного форматирования текста
def text_color(
        text: str,
        *codes: int
) -> str:
    return text if codes == [] else f"\033[{';'.join([str(s) for s in codes])}m{text}\033[0m"


def text_error(text: str) -> str:
    return text_color(f'\n Error: {text} \n\n', COLOR_TEXT_BLACK, COLOR_BG_RED)


def text_success(text: str) -> str:
    return text_color(f'\n {text} ', COLOR_TEXT_GREEN)


class Command:
    def __init__(self, command: str, stderr=subprocess.PIPE):
        self.__command = command
        self.__process = None
        self.__output = None
        self.__error = None
        self.__stderr = stderr

    def run(self) -> 'Command':
        self.__process = subprocess.Popen(
            self.__command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=self.__stderr,
            universal_newlines=True
        )
        output, error = self.__process.communicate()

        if output is not None:
            self.__output = output.strip()
        if error is not None:
            self.__error = error.strip()
        return self

    def get_output(self) -> str | None:
        return self.__output

    def get_error(self) -> str | None:
        if self.__error is None:
            return None
        error = ''
        pattern = r'msg="((?:[^"\\]|\\.)*)"'
        for line in self.__error.split('\n'):
            match = re.search(pattern, line)
            error += match.group(1) + '\n' if match else line + '\n'
        return error

    def get_code(self):
        return self.__process.returncode if self.__process else None


def execute_command(command):
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    output, _ = process.communicate()
    return output.strip()
