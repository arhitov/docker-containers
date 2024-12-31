from libs.i18n import trans


def ask_question(question) -> bool:
    while True:
        answer = input(f"{question} (Yes/No): ").lower().strip()
        if answer == 'yes' or answer == 'y':
            return True
        elif answer == 'no' or answer == 'n':
            return False
        else:
            print(trans('Please enter "Yes" or "No".'))
