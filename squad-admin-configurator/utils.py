from django.urls import reverse


def reverse_to_admin_edit(obj):
    return reverse(
        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
        args=[obj.id]
    )
