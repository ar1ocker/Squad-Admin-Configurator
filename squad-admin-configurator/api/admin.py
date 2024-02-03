from django.contrib import admin
from django.contrib.admin.filters import AllValuesFieldListFilter
from django.urls import reverse
from django.utils.html import format_html
from utils import reverse_to_admin_edit, textarea_form

from .admin_actions import create_local_config
from .models import AdminsConfigDistribution, RoleWebhook, WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "message",
        "webhook_info",
        "request_info",
        "level",
        "creation_date",
        "content_type",
        "object_id",
        "content_object_link",
    )
    readonly_fields = ("id", "creation_date", "content_object_link")
    list_display = (
        "level",
        "message_display",
        "creation_date",
        "content_object_link",
    )
    list_filter = (
        "creation_date",
        "content_type",
        ("level", AllValuesFieldListFilter),
    )

    @admin.display(description="Сообщение")
    def message_display(self, obj):
        return obj.message[:100]

    @admin.display(description="Объект записавший лог", empty_value="-")
    def content_object_link(self, obj):
        if obj.content_object is None:
            return None

        return format_html(
            '<a href="{}">{}</a>',
            reverse_to_admin_edit(obj.content_object),
            str(obj.content_object),
        )


@admin.register(RoleWebhook)
class RoleWebhookAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "is_active",
                    "description",
                    "url",
                    "creation_date",
                    "servers",
                    "roles",
                    ("unit_of_duration", "duration_until_end"),
                    "allow_custom_duration_until_end",
                    "active_and_increase_common_date_of_end",
                ],
                "description": (
                    "При запросе данных вебхуков - на установленных "
                    "ниже серверах будут выданы"
                    " роли, запрос должен быть в формате json и "
                    'содержать поля "steam_id", "name" (имя, которым'
                    " будет назван пользователь если не будет "
                    'найден по "steam_id"), "comment" и '
                    '"duration_until_end" (время на которое '
                    "выдается роль, если разрешено устанавливать "
                    "время в запросе)"
                ),
            },
        ),
        (
            "Проверка HMAC",
            {
                "classes": ["collapse"],
                "fields": [
                    "hmac_is_active",
                    ("hmac_hash_type", "hmac_secret_key"),
                    ("hmac_header", "hmac_header_regex"),
                    "request_sender",
                ],
                "description": (
                    "HMAC - это фактически подпись, которая "
                    "позволяет убедиться, что запрос пришел от "
                    "того, у кого есть секретный ключ"
                ),
            },
        ),
    ]

    readonly_fields = ("creation_date",)
    list_display = ("description", "is_active", "url", "hmac_is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    filter_horizontal = ("servers", "roles")

    def save_model(self, request, obj, form, change):
        """Отправка сообщений с текущим полным url к вебхуку"""
        if obj.is_active:
            self.message_user(
                request,
                "Путь к вебхуку "
                + request.build_absolute_uri(
                    reverse("api:role_webhook", args=(obj.url,))
                ),
            )
        return super().save_model(request, obj, form, change)


@admin.register(AdminsConfigDistribution)
class AdminsConfigAdmin(admin.ModelAdmin):
    form = textarea_form(AdminsConfigDistribution, ["description"])
    fields = [
        "is_active",
        "title",
        "server",
        "description",
        "type_of_distribution",
        "local_filename",
        "url",
    ]
    list_display = [
        "is_active",
        "title",
        "type_of_distribution",
        "local_filename",
        "url",
    ]
    list_editable = ["is_active"]
    list_display_links = ["title"]
    list_filter = ["is_active", "type_of_distribution"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["server"]
    actions = ["update_config"]

    def save_model(self, request, obj, form, change):
        """Отправка сообщений с текущим полным url к конфигурации"""
        if (
            obj.is_active
            and obj.type_of_distribution
            in AdminsConfigDistribution.TYPES_OF_DISTRIBUTION_WITH_API
        ):
            self.message_user(
                request,
                "Путь к файлу "
                + request.build_absolute_uri(
                    reverse("api:server_config", args=(obj.url,))
                ),
            )
        return super().save_model(request, obj, form, change)

    @admin.action(description="Обновление локального конфига")
    def update_config(self, request, queryset):
        for obj in queryset:
            create_local_config(obj)
        self.message_user(request, "Обновили выбранные конфиги")
