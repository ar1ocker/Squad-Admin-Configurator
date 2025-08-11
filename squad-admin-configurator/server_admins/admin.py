from datetime import datetime

import adminactions.actions as actions
from access.admin import AccessModelAdmin
from django.contrib import admin
from django.contrib.admin import site
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeText, mark_safe
from server_admins.models import (
    Permission,
    Privileged,
    Role,
    Server,
    ServerPrivileged,
    ServerPrivilegedPack,
)
from server_admins.utils import date_or_perpetual

# Регистрация всех action из adminactions
actions.add_to_site(site)


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs) -> admin.FieldListFilter:
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class ServerPrivilegedInline(admin.StackedInline):
    fields = (
        "is_active",
        "creation_date",
        "date_of_end",
        "server",
        "roles",
        "privileged",
        "comment",
    )
    readonly_fields = ("creation_date",)
    model = ServerPrivileged
    extra = 0
    verbose_name_plural = "Роли на серверах"


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "is_active",
    )
    list_editable = ("is_active",)
    search_fields = (
        "title",
        "description",
    )
    ordering = ("-title",)
    list_filter = ("is_active",)


@admin.register(ServerPrivileged)
class ServerPrivilegedAdmin(admin.ModelAdmin):
    fields = (
        "is_active",
        "privileged",
        "server",
        "roles",
        "creation_date",
        "date_of_end",
    )
    readonly_fields = ("creation_date",)
    list_display = (
        "is_active",
        "privileged",
        "server",
        "get_roles",
        "creation_date",
        "date_of_end_view",
    )
    list_display_links = ("privileged", "server")
    list_editable = ("is_active",)
    list_filter = (
        (
            "server__title",
            custom_titled_filter("Название сервера"),
        ),
        (
            "privileged__is_active",
            custom_titled_filter("Пользователь активирован"),
        ),
        "is_active",
        "roles",
        "date_of_end",
        "creation_date",
    )
    ordering = ("-creation_date",)
    search_fields = ("privileged__steam_id", "privileged__name")

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Дата окончания полномочий",
    )
    def date_of_end_view(self, obj):
        return obj.date_of_end

    @admin.display(description="Роли на сервере")
    def get_roles(self, obj) -> str:
        return ", ".join((role.title for role in obj.roles.all()))

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return ServerPrivileged.objects.prefetch_related("roles")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "is_active")
    list_editable = ("is_active",)
    filter_vertical = ("permissions",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )


@admin.register(Privileged)
class PrivilegedAdmin(admin.ModelAdmin):
    inlines = (ServerPrivilegedInline,)
    fields = (
        "is_active",
        "name",
        "steam_id",
        "description",
        "creation_date",
        "date_of_end",
    )
    readonly_fields = ("creation_date",)
    list_display = (
        "name",
        "get_roles",
        "profile",
        "is_active",
        "date_of_end_view",
        "creation_date",
    )
    list_editable = ("is_active",)
    list_filter = (
        "is_active",
        "server_accesses__roles",
        (
            "server_accesses__is_active",
            custom_titled_filter("Есть активированные привилегии на серверах"),
        ),
        "date_of_end",
        "creation_date",
    )
    ordering = ("-creation_date",)
    search_fields = ("name", "steam_id", "description")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return Privileged.objects.prefetch_related("server_accesses__roles", "server_accesses__server")

    @admin.display(description="Профиль Steam")
    def profile(self, obj):
        return format_html(
            '<a href="https://steamcommunity.com/profiles/{0}" target="_blank">Профиль {0}</a>', obj.steam_id
        )

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Общая дата окончания полномочий",
    )
    def date_of_end_view(self, obj):
        return obj.date_of_end

    @admin.display(description="Роли на всех серверах")
    def get_roles(self, obj) -> str:
        servers_text = []

        not_active_privs_count = 0

        for access in obj.server_accesses.all():
            if not access.is_active:
                not_active_privs_count += 1
                continue

            symbol = "🟢"
            date_of_end = date_or_perpetual(access.date_of_end)
            roles = ", ".join((role.title for role in access.roles.all()))

            servers_text.append(f"{symbol} {access.server.title} ({date_of_end}): {roles}")

        if not_active_privs_count:
            servers_text.append(f"Неактивных привилегий: {not_active_privs_count}")

        return format_html_join(
            mark_safe("<br>"),
            "{}",
            ((i,) for i in servers_text),
        )


@admin.register(ServerPrivilegedPack)
class ServerPrivilegedPackAdmin(AccessModelAdmin):
    fields_for_moderator = ("steam_ids",)
    fields = (
        "title",
        "is_active",
        "steam_ids",
        "servers",
        "roles",
        "max_ids",
        "moderators",
        "creation_date",
        "date_of_end",
        "comment",
    )
    readonly_fields = ("creation_date",)
    list_display = (
        "is_active",
        "title",
        "get_servers",
        "max_ids",
        "creation_date",
        "date_of_end_view",
    )
    list_display_links = ("title", "get_servers")
    list_filter = (
        (
            "servers__title",
            custom_titled_filter("Название сервера"),
        ),
        "is_active",
        "roles",
        "date_of_end",
        "creation_date",
    )
    ordering = ("-creation_date",)
    search_fields = ("steam_ids", "servers__title")

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Дата окончания полномочий",
    )
    def date_of_end_view(self, obj: ServerPrivilegedPack) -> datetime | None:
        return obj.date_of_end

    @admin.display(description="Сервера")
    def get_servers(self, obj) -> SafeText | str:
        servers = obj.servers.all()
        if len(servers) == 0:
            return ""

        return format_html_join(
            mark_safe("<br>"),
            "{}",
            [(server.title for server in servers)],
        )

    def get_readonly_fields(self, request, obj: ServerPrivilegedPack | None = None):
        if request.user.is_superuser or obj is None:
            return super().get_readonly_fields(request, obj)

        if obj.moderators.filter(pk=request.user.pk).exists():
            return set(self.fields) - set(self.fields_for_moderator)

        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        return ServerPrivilegedPack.objects.prefetch_related("servers")
