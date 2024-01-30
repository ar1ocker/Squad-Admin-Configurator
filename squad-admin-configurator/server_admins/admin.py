from django.contrib import admin, messages

from .admin_actions import create_local_config, create_local_configs
from .models import Permission, Privileged, Role, Server, ServerPrivileged
from .utils import date_or_perpetual


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
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


@admin.register(Server)
class AdminServer(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "is_active",
        "type_of_distribution",
        "local_filename",
    )
    list_editable = ("is_active",)
    search_fields = (
        "title",
        "description",
    )
    ordering = ("-title",)
    list_filter = ("is_active", "type_of_distribution")
    actions = ("create_admins_cfg", "create_admins_cfg_selected")

    @admin.action(description="Обновить все конфиги", permissions=["change"])
    def create_admins_cfg(self, request, queryset):
        create_local_configs()
        self.message_user(request, "Конфиги обновлены", messages.SUCCESS)

    @admin.action(
        description="Обновить конфиг выбранных серверов",
        permissions=["change"],
    )
    def create_admins_cfg_selected(self, request, queryset):
        for server in queryset:
            create_local_config(server)
        self.message_user(
            request, "Выбранные сервера обновлены", messages.SUCCESS
        )


@admin.register(Role)
class AdminRole(admin.ModelAdmin):
    list_display = ("title", "description", "is_active")
    list_editable = ("is_active",)
    filter_horizontal = ("permissions",)


@admin.register(Permission)
class AdminPermission(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )


@admin.register(Privileged)
class AdminPrivileged(admin.ModelAdmin):
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
    actions = ("create_admins_cfg",)

    @admin.display(
        ordering="-date_of_end",
        empty_value="Бессрочно",
        description="Общая дата окончания полномочий",
    )
    def date_of_end_view(self, obj):
        return obj.date_of_end

    @admin.action(description="Обновить все конфиги", permissions=["change"])
    def create_admins_cfg(self, request, queryset):
        create_local_configs()
        self.message_user(request, "Конфиги обновлены", messages.SUCCESS)

    @admin.display(description="Роли на всех серверах")
    def get_roles(self, obj):
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
