from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django_cron import CronJobBase, Schedule

from .models import RotationDistribution


class CreateRotationsFiles(CronJobBase):
    schedule = Schedule(run_every_mins=2)
    code = "Обновление локальных файлов с ротациями"

    def do(self):
        now = timezone.now()

        rot_distributions = RotationDistribution.objects.select_related("rotation").filter(
            is_active=True,
            type_of_distribution__in=RotationDistribution.TYPES_OF_DISTRIBUTION_WITH_LOCAL,
        )

        settings.ROTATIONS_CONFIG_DIR.mkdir(exist_ok=True)

        with transaction.atomic():
            for distrib in rot_distributions:
                pack = distrib.get_current_pack()
                if pack is None:
                    pack = distrib.get_next_pack_by_queue()
                else:
                    last_update_date_pass = (
                        (distrib.last_update_date.date() != now.date()) if distrib.last_update_date else True
                    )

                    is_need_next_pack = distrib.last_queue_number == pack.queue_number and last_update_date_pass

                    if is_need_next_pack:
                        pack = distrib.get_next_pack_by_queue()

                with open(
                    settings.ROTATIONS_CONFIG_DIR / distrib.local_filename,
                    "w",
                    encoding="utf-8",
                ) as file:
                    file.write(distrib.format_config(pack))

                distrib.last_update_date = now

                if pack and pack.queue_number is not None:
                    distrib.last_queue_number = pack.queue_number

                distrib.save()
