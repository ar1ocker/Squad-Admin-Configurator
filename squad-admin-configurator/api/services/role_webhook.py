from datetime import datetime, timedelta

from api.models import RoleWebhook
from django.db import transaction
from django.db.models import Count, F, Q, QuerySet
from django.utils import timezone
from server_admins.models import Privileged, Role, Server, ServerPrivileged


# TODO РЕФАКТОРИТЬ!!!
def role_webhook__create_server_privileges(*, webhook: RoleWebhook, validated_data: dict):
    steam_id = validated_data["steam_id"]
    name = validated_data["name"]
    description = validated_data["comment"]
    duration_until_end = _select_duration(webhook=webhook, duration_until_end=validated_data["duration_until_end"])
    date_of_end = _get_date_of_end(webhook, duration_until_end)

    priv_defaults = {
        "name": name,
        "description": description,
    }

    if webhook.set_common_date_of_end:
        priv_defaults["date_of_end"] = date_of_end

    priv, priv_created = Privileged.objects.get_or_create(
        steam_id=steam_id,
        defaults=priv_defaults,
    )

    servers_for_add = [server for server in webhook.servers.all()]

    existed_server_privileges = []

    if webhook.try_to_increase_existing_record:
        existed_server_privileges = _search_server_privileges_with_exact_roles(
            privileged=priv, servers=webhook.servers, roles=webhook.roles
        )

        for existed_server_priv in existed_server_privileges:
            servers_for_add.remove(existed_server_priv.server)

    with transaction.atomic():
        if not priv_created and webhook.active_and_increase_common_date_of_end:
            _active_and_increase_privileged(privileged=priv, new_date_of_end=date_of_end)

        roles_ids = webhook.roles.values_list("pk", flat=True)

        for server in servers_for_add:
            server_priv = ServerPrivileged.objects.create(
                server=server,
                privileged=priv,
                date_of_end=date_of_end,
                comment=validated_data["comment"],
            )

            server_priv.roles.add(*roles_ids)

        for server_priv in existed_server_privileges:
            if server_priv.date_of_end is None:
                continue

            if duration_until_end is None:
                server_priv.date_of_end = None
            else:
                server_priv.date_of_end = server_priv.date_of_end + timedelta_from_duration(
                    unit=webhook.unit_of_duration, duration=duration_until_end
                )

            server_priv.save()


def _search_server_privileges_with_exact_roles(
    *, privileged: Privileged, servers: QuerySet[Server], roles: QuerySet[Role]
):
    roles_count = roles.count()

    existed_server_privileges = (
        ServerPrivileged.objects.filter(privileged=privileged, server__in=servers.all(), is_active=True)
        .annotate(
            num_roles=Count("roles", distinct=True),
            matching_roles=Count("roles", distinct=True, filter=Q(roles__in=roles.all())),
        )
        .filter(num_roles=roles_count, matching_roles=roles_count)
    ).order_by(F("date_of_end").desc(nulls_first=True))

    unique_server_priv_with_servers: dict[int, ServerPrivileged] = {}

    for server_priv in existed_server_privileges:
        if server_priv.server_id not in unique_server_priv_with_servers:
            unique_server_priv_with_servers[server_priv.server_id] = server_priv

    return list(unique_server_priv_with_servers.values())


def _active_and_increase_privileged(*, privileged: Privileged, new_date_of_end: datetime | None):
    need_save = False
    if not privileged.is_active:
        privileged.is_active = True
        need_save = True

    if privileged.date_of_end is not None and new_date_of_end is None:
        privileged.date_of_end = new_date_of_end
        need_save = True
    elif privileged.date_of_end is not None and privileged.date_of_end < new_date_of_end:
        privileged.date_of_end = new_date_of_end
        need_save = True

    if need_save:
        privileged.save()


def _select_duration(*, webhook: RoleWebhook, duration_until_end: int | None) -> int | None:
    if webhook.allow_custom_duration_until_end and duration_until_end:
        return duration_until_end
    else:
        return webhook.duration_until_end


def _get_date_of_end(webhook: RoleWebhook, duration: int | None) -> None | datetime:
    if duration is None:
        return None

    return timezone.now() + timedelta_from_duration(unit=webhook.unit_of_duration, duration=duration)


def timedelta_from_duration(*, unit: str, duration: int) -> timedelta:
    return timedelta(**{unit: duration})
