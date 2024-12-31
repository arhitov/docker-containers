from libs.i18n import trans


def str_to_bool(s: str | bool) -> bool:
    if isinstance(s, bool):
        return s
    elif s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise ValueError(trans('Unknown line: :1', s))
