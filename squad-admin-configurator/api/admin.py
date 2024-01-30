from django.contrib import admin
from django.contrib.admin.filters import AllValuesFieldListFilter
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from server_admins.models import Server
from utils import reverse_to_admin_edit

from .models import RoleWebhook, ServerUrl, WebhookLog


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


@admin.register(ServerUrl)
class ServerUrlAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Убираем из выбора серверов не подходящие или уже использованные
        варианты
        """
        if db_field.name == "server":
            server_url_id = request.resolver_match.kwargs.get("object_id")
            its_our_server = Q(server_url=server_url_id)
            with_api_and_not_tied = Q(
                type_of_distribution__in=Server.TYPES_OF_DISTRIBUTION_WITH_API
            ) & Q(  # noqa: E501
                server_url=None
            )

            kwargs["queryset"] = Server.objects.filter(
                its_our_server | with_api_and_not_tied
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Отправка сообщений с текущим полным url к конфигурации"""
        if obj.is_active:
            self.message_user(
                request,
                "Путь к файлу "
                + request.build_absolute_uri(
                    reverse("api:server_config", args=(obj.url,))
                ),
            )
        return super().save_model(request, obj, form, change)

    fields = ("is_active", "server", "url")
    list_display = ("server", "is_active", "url")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
