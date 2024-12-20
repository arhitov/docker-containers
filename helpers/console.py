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
    return text_color(f'\n Ошибка: {text} \n\n', COLOR_TEXT_BLACK, COLOR_BG_RED)


def text_success(text: str) -> str:
    return text_color(f'\n {text} ', COLOR_TEXT_GREEN)
