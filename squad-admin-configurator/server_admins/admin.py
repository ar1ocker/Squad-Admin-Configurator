import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site

from .models import Permission, Privileged, Role, Server, ServerPrivileged
from .utils import date_or_perpetual

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
        ("is_active", "creation_date", "date_of_end"),
        "server",
        "roles",
        "privileged",
        "comment",
    )
    readonly_fields = ("creation_date",)
    filter_horizontal = ("roles",)
    model = ServerPrivileged
    extra = 0
    autocomplete_fields = ("server",)
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
        "is_active",
        "privileged__is_active",
        "roles",
        "date_of_end",
        "creation_date",
    )
    ordering = ("-creation_date",)
    search_fields = ("privileged__steam_id", "privileged__name")
    autocomplete_fields = ("server", "privileged")
    filter_horizontal = ("roles",)

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Дата окончания полномочий",
    )
    def date_of_end_view(self, obj):
        return obj.date_of_end

    @admin.display(description="Роли на сервере")
    def get_roles(self, obj) -> str:
        return ", ".join(obj.roles.values_list("title", flat=True))


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "is_active")
    list_editable = ("is_active",)
    filter_horizontal = ("permissions",)


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
        "is_active",
        "date_of_end_view",
        "creation_date",
    )
    list_editable = ("is_active",)
    list_filter = (
        "is_active",
        "servers_roles",
        "serverprivileged__roles",
        (
            "serverprivileged__is_active",
            custom_titled_filter("Есть активированные привилегии на серверах"),
        ),
        "date_of_end",
        "creation_date",
    )
    ordering = ("-creation_date",)
    search_fields = ("name", "steam_id", "description")

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Общая дата окончания полномочий",
    )
    def date_of_end_view(self, obj):
        return obj.date_of_end

    @admin.display(description="Роли на всех серверах")
    def get_roles(self, obj) -> str:
        servers_roles = obj.serverprivileged_set.select_related(
            "server"
        ).prefetch_related("roles")
        servers_text = []
        for serv in servers_roles:
            symbol = "🟢" if serv.is_active else "🔴"
            date_of_end = date_or_perpetual(serv.date_of_end)
            roles = ", ".join(serv.roles.values_list("title", flat=True))

            servers_text.append(
                f"{symbol} {serv.server.title} ({date_of_end}): {roles}"
            )

        return "; ".join(servers_text)
