from django.conf import settings
from django_cron import CronJobBase, Schedule

from .admin_actions import create_local_configs

EXPIRED_PRIVILEGED_CHAT = settings.DISCORD["EXPIRED_PRIVILEGED_CHAT"]


class CreateAdminsConfig(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = "Обновление локальных файлов администраторов"

    def do(self) -> None:
        create_local_configs()
