from django.conf import settings
from django.utils import timezone
from django_cron import CronJobBase, Schedule
from utils import reverse_to_admin_edit

from .admin_actions import create_local_configs
from .discord import send_messages_to_discord
from .models import Privileged, ServerPrivileged

EXPIRED_PRIVILEGED_CHAT = settings.DISCORD['EXPIRED_PRIVILEGED_CHAT']


class CreateAdminsConfig(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = 'Обновление локальных файлов администраторов'

    def do(self):
        create_local_configs()


class DisablingServerPrivilegedByEndTime(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = (
        'Изменение поля is_active у пользователя по роли на конкретном сервере'
    )

    def do(self):
        server_privileges = (
            ServerPrivileged.objects
            .filter(date_of_end__lt=timezone.now(), is_active=True)
            .exclude(date_of_end=None)
            .select_related('server', 'privileged')
            .prefetch_related('roles')
        )

        for server_priv in server_privileges:
            server_priv.is_active = False
            server_priv.save()

        if server_privileges.count() > 0:
            self.send_info(server_privileges)

    def send_info(self, server_privileges):
        if not EXPIRED_PRIVILEGED_CHAT['ENABLE']:
            return

        messages = []
        for server_priv in server_privileges:
            roles_text = ', '.join(
                [role.title for role in server_priv.roles.all()]
            )

            messages.append(
                f'{settings.BASE_URL}'
                f'{reverse_to_admin_edit(server_priv.privileged)}\n'
                f'{server_priv.privileged.name} - '
                f'{server_priv.privileged.steam_id}\n'
                'Истекли полномочия на сервере:\n'
                f'{server_priv.server.title} - {roles_text}'
            )

        send_messages_to_discord(
            EXPIRED_PRIVILEGED_CHAT['CHAT_WEBHOOK'], 'Админ панель', messages
        )


class DisablingPrivilegedByEndTime(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = ('Изменение поля is_active у пользователей по '
            'истечению времени полномочий и информирование в дискорд')

    def do(self):
        privileges = (
            Privileged.objects
            .filter(date_of_end__lt=timezone.now(), is_active=True)
            .exclude(date_of_end=None)
            .prefetch_related('serverprivileged_set__roles',
                              'serverprivileged_set__server')
        )

        for priv in privileges:
            priv.is_active = False
            priv.save()

        if privileges.count() > 0:
            self.send_info(privileges)

    def send_info(self, privileges):
        if not EXPIRED_PRIVILEGED_CHAT['ENABLE']:
            return

        messages = []
        for priv in privileges:
            all_roles_text = []
            for server_roles in priv.serverprivileged_set.all():
                roles_text = ', '.join(
                    [role.title for role in server_roles.roles.all()]
                )

                all_roles_text.append(
                    f'{server_roles.server.title} - {roles_text};'
                )

            messages.append(
                f'{settings.BASE_URL}{reverse_to_admin_edit(priv)}\n'
                f'{priv.name} - {priv.steam_id}\n'
                'Истекли все полномочия:\n'
                + ' '.join(all_roles_text)
            )

        send_messages_to_discord(
            EXPIRED_PRIVILEGED_CHAT['CHAT_WEBHOOK'], 'Админ панель', messages
        )
