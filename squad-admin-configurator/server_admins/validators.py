import re

from django.core.exceptions import ValidationError


def admins_filename_validator(
    value,
    error_field,
    error_message="Введите валидное имя файла [A-Za-z0-9_-], первый и последний символ только буквы, несколько тире и подчеркиваний подряд запрещены",
):
    result = re.search(
        r"^(?!.*[_-][_-])[A-Za-z][A-Za-z0-9_\-]{1,18}[A-Za-z0-9]$", value
    )

    if result is None:
        raise ValidationError({error_field: error_message})
