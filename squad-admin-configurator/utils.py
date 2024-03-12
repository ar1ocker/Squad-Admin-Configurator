import re

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse


def reverse_to_admin_edit(obj) -> str:
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.id],
    )


def textarea_form(model, fields: list):
    """
    Генератор классов ModelForm заменяющих стандартный виджет любого поля
    на Textarea для указанных полей
    """
    meta = type(
        "Meta",
        (),
        {
            "fields": "__all__",
            "model": model,
            "widgets": {field: forms.Textarea() for field in fields},
        },
    )

    return type("TextAreaForFields", (forms.ModelForm,), {"Meta": meta})


def filename_validator(value) -> None:
    if value is not None and not re.fullmatch(r"^(?!.*[_-][_-])[A-Za-z0-9_]+$", value):
        raise ValidationError(
            "Только латинские буквы, цифры и знак подчеркивания, множественные знаки подчеркивания запрещены"
        )


def regex_validator(value) -> None:
    try:
        re.compile(value)
    except re.error as e:
        raise ValidationError(f"Не валидное регулярное выражение, {e}")


def url_postfix_validator(value) -> None:
    if value is not None and not re.fullmatch("[A-Za-z0-9_]+", value):
        raise ValidationError("Только латинские буквы, цифры и знак подчеркивания")
