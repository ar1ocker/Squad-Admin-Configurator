import django_filters
from server_admins.models import Privileged, Role, Server, ServerPrivileged


class ServerFilter(django_filters.FilterSet):
    privileged_steam_id = django_filters.NumberFilter("privileged_accesses__privileged__steam_id", distinct=True)
    privileged_name = django_filters.CharFilter("privileged_accesses__privileged__name", "icontains", distinct=True)
    title = django_filters.CharFilter("title", "icontains")

    class Meta:
        model = Server
        fields = (
            "is_active",
            "title",
            "description",
        )


class RoleFilter(django_filters.FilterSet):
    privileged_steam_id = django_filters.NumberFilter(
        "privileged_accesses__privileged__steam_id",
        distinct=True,
        label="Steam ID пользователя у которого есть связь с ролью",
    )
    privileged = django_filters.ModelChoiceFilter(
        "privileged_accesses__privileged", queryset=Privileged.objects.all(), distinct=True, label="ID пользователя"
    )
    permission = django_filters.CharFilter(
        "permissions__title", "icontains", distinct=True, label="Названия разрешений"
    )
    title = django_filters.CharFilter("title", "icontains", label="Название роли")

    is_active = django_filters.BooleanFilter(label="Активирована ли роль")

    class Meta:
        model = Role
        fields = ("is_active",)


class PrivilegedFilter(django_filters.FilterSet):
    name = django_filters.CharFilter("name", "icontains", label="Имя")
    description = django_filters.CharFilter("description", "icontains", label="Описание")

    class Meta:
        model = Privileged
        fields = ("name", "steam_id", "is_active", "description")


class ServerPrivilegedFilter(django_filters.FilterSet):
    server_title = django_filters.CharFilter("server__title", "icontains", label="Название сервера")
    server_is_active = django_filters.BooleanFilter("server__is_active", label="Активирован ли сервер")
    privileged_steam_id = django_filters.NumberFilter("privileged__steam_id", label="Steam ID пользователя")
    privileged_is_active = django_filters.BooleanFilter("privileged__is_active", label="Активирован ли пользователь")
    roles = django_filters.BaseInFilter(field_name="roles", lookup_expr="in")

    class Meta:
        model = ServerPrivileged
        fields = ("server", "privileged")
