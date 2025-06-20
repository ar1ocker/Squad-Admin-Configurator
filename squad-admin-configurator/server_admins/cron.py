from discord_message import send_messages_to_discord
from django.conf import settings
from django.utils import timezone
from django_cron import CronJobBase, Schedule
from utils import reverse_to_admin_edit

from .models import Privileged, ServerPrivileged, ServerPrivilegedPack

EXPIRED_PRIVILEGED_CHAT = settings.DISCORD["EXPIRED_PRIVILEGED_CHAT"]


class DisablingServerPrivilegedByEndTime(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = "Изменение поля is_active у пользователя"

    def do(self) -> None:
        server_privileges = (
            ServerPrivileged.objects.filter(date_of_end__lt=timezone.now(), is_active=True)
            .exclude(date_of_end=None)
            .select_related("server", "privileged")
            .prefetch_related("roles")
        )

        for server_priv in server_privileges:
            server_priv.is_active = False
            server_priv.save()

        if server_privileges.count() > 0:
            self.send_info(server_privileges)

    def send_info(self, server_privileges) -> None:
        if not EXPIRED_PRIVILEGED_CHAT["ENABLE"]:
            return

        messages: list[str] = []
        for server_priv in server_privileges:
            roles_text: str = ", ".join([role.title for role in server_priv.roles.all()])

            messages.append(
                f"{settings.BASE_URL}"
                f"{reverse_to_admin_edit(server_priv.privileged)}\n"
                f"{server_priv.privileged.name} - "
                f"{server_priv.privileged.steam_id}\n"
                "Истекли полномочия на сервере:\n"
                f"{server_priv.server.title} - {roles_text}"
            )

        send_messages_to_discord(EXPIRED_PRIVILEGED_CHAT["CHAT_WEBHOOK"], "Админ панель", messages)


class DisablingPrivilegedByEndTime(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = "Изменение поля is_active у serverprivileged"

    def do(self):
        privileges = (
            Privileged.objects.filter(date_of_end__lt=timezone.now(), is_active=True)
            .exclude(date_of_end=None)
            .prefetch_related("serverprivileged_set__roles", "serverprivileged_set__server")
        )

        for priv in privileges:
            priv.is_active = False
            priv.save()

        if privileges.count() > 0:
            self.send_info(privileges)

    def send_info(self, privileges):
        if not EXPIRED_PRIVILEGED_CHAT["ENABLE"]:
            return

        messages = []
        for priv in privileges:
            all_roles_text = []
            for server_roles in priv.serverprivileged_set.all():
                roles_text = ", ".join([role.title for role in server_roles.roles.all()])

                all_roles_text.append(f"{server_roles.server.title} - {roles_text};")

            messages.append(
                f"{settings.BASE_URL}{reverse_to_admin_edit(priv)}\n"
                f"{priv.name} - {priv.steam_id}\n"
                "Истекли все полномочия:\n" + " ".join(all_roles_text)
            )

        send_messages_to_discord(EXPIRED_PRIVILEGED_CHAT["CHAT_WEBHOOK"], "Админ панель", messages)


class DisablingServerPrivilegedPacksByEndTime(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = "Изменение поля is_active у паков"

    def do(self) -> None:
        server_packs = (
            ServerPrivilegedPack.objects.filter(date_of_end__lt=timezone.now(), is_active=True)
            .exclude(date_of_end=None)
            .prefetch_related("roles", "servers")
        )

        for server_pack in server_packs:
            server_pack.is_active = False
            server_pack.save()

        if server_packs.count() > 0:
            self.send_info(server_packs)

    def send_info(self, server_packs) -> None:
        if not EXPIRED_PRIVILEGED_CHAT["ENABLE"]:
            return

        messages: list[str] = []
        for pack in server_packs:
            roles_text: str = ", ".join([role.title for role in pack.roles.all()])
            servers_text: str = ", ".join([server.title for server in pack.servers.all()])

            messages.append(
                f"{settings.BASE_URL}"
                f"{reverse_to_admin_edit(pack)}\n"
                f"Пак {pack.name}\n"
                "Истекли полномочия на серверах:\n"
                f"{servers_text} - {roles_text}"
            )

        send_messages_to_discord(EXPIRED_PRIVILEGED_CHAT["CHAT_WEBHOOK"], "Админ панель", messages)
