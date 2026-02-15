from collections import defaultdict

from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from server_admins.models import Server, ServerPrivileged, ServerPrivilegedPack
from server_admins.steam_ids_parser import SteamIDsSpec


def server__generate_config(*, server: Server) -> str:

    now = timezone.now()

    if not server.is_active:
        return render_to_string(
            "server_config/admins_inactive.django",
            {"server": server, "now_date": now.strftime(settings.DATETIME_FORMAT)},
        )

    server_privileges = (
        ServerPrivileged.objects.filter(
            Q(date_of_end__gte=now) | Q(date_of_end=None),
            Q(privileged__date_of_end__gte=now) | Q(privileged__date_of_end=None),
            privileged__is_active=True,
            is_active=True,
            server=server,
        )
        .select_related("privileged")
        .prefetch_related("roles__permissions")
    )

    server_privileged_packs = ServerPrivilegedPack.objects.filter(
        Q(date_of_end__gte=now) | Q(date_of_end=None), is_active=True, servers=server
    ).prefetch_related("roles__permissions")

    roles_with_permissions = {}
    privileged_by_role = defaultdict(list)
    packs_by_role = defaultdict(list)

    for server_priv in server_privileges:
        for role in server_priv.roles.all():
            if not role.is_active:
                continue

            if role not in roles_with_permissions:
                permissions: str = ",".join([perm.title for perm in role.permissions.all()])
                roles_with_permissions[role] = permissions

            privileged_by_role[role].append(server_priv.privileged)

    for server_pack in server_privileged_packs:
        for role in server_pack.roles.all():
            if not role.is_active:
                continue

            if role not in roles_with_permissions:
                permissions: str = ",".join([perm.title for perm in role.permissions.all()])
                roles_with_permissions[role] = permissions

            parsed_steam_ids = SteamIDsSpec.parse(server_pack.steam_ids)

            steam_ids = [
                node.value for node in filter(lambda node: node.kind == SteamIDsSpec.STEAMID.name, parsed_steam_ids)
            ]

            packs_by_role[role].append({"title": server_pack.title, "steam_ids": steam_ids})

    packs_by_role.default_factory = None
    privileged_by_role.default_factory = None

    return render_to_string(
        "server_config/admins_active.django",
        {
            "server": server,
            "now_date": now.strftime(settings.DATETIME_FORMAT),
            "roles_with_permissions": roles_with_permissions,
            "privileged_by_role": privileged_by_role,
            "packs_by_role": packs_by_role,
        },
    )
