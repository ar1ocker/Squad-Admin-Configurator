from django import forms
from django.urls import reverse


def reverse_to_admin_edit(obj):
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=[obj.id],
    )


def textarea_form(model, fields: list):
    """Генератор классов ModelForm заменяющих стандартный виджет любого поля на Textarea для указанных полей"""
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
