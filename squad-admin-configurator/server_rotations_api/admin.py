from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from utils import textarea_form

from .models import RotationDistribution


@admin.register(RotationDistribution)
class RotationDistributionAdmin(admin.ModelAdmin):
    form = textarea_form(RotationDistribution, ["description"])
    fields = [
        "is_active",
        "title",
        "rotation",
        "description",
        "type_of_distribution",
        "local_filename",
        "url",
        "last_update_date",
        "last_queue_number",
    ]
    list_display = [
        "is_active",
        "title",
        "type_of_distribution",
        "last_queue_number",
        "last_update_date",
        "local_filename",
        "url",
    ]
    list_editable = ["is_active"]
    list_display_links = ["title"]
    list_filter = ["is_active", "type_of_distribution"]
    search_fields = ["title", "description"]

    def save_model(self, request, obj, form, change):
        """Отправка сообщений с текущим полным url к конфигурации"""
        if obj.is_active and obj.type_of_distribution in RotationDistribution.TYPES_OF_DISTRIBUTION_WITH_API:
            self.message_user(
                request,
                format_html(
                    '<a href="{0}" target="_blank">Ссылка на текущий файл - {0}</a>',
                    request.build_absolute_uri(reverse("rotations_api:current_rotation_config", args=(obj.url,))),
                ),
            )

            self.message_user(
                request,
                format_html(
                    '<a href="{0}" target="_blank">Ссылка на следующий файл - {0}</a>',
                    request.build_absolute_uri(reverse("rotations_api:next_rotation_config", args=(obj.url,))),
                ),
            )

        return super().save_model(request, obj, form, change)
