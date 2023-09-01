import re
from django.core.exceptions import ValidationError


def regex_validator(value):
    try:
        re.compile(value)
    except re.error as e:
        raise ValidationError(f'Не валидное регулярное выражение, {e}')


def url_postfix_validator(value):
    if not re.fullmatch('[A-Za-z0-9_]+', value):
        raise ValidationError(
            'Только латинские буквы, цифры и знак подчеркивания ([A-Za-z0-9_]+)'
        )
