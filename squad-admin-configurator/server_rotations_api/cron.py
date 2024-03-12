from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django_cron import CronJobBase, Schedule

from .models import RotationDistribution


class CreateRotationsFiles(CronJobBase):
    schedule = Schedule(run_every_mins=60)
    code = "Обновление локальных файлов с ротациями"

    def do(self):
        now = timezone.now()
        local_types = RotationDistribution.TYPES_OF_DISTRIBUTION_WITH_LOCAL
        rot_distributions = RotationDistribution.objects.select_related("rotation").filter(
            ~Q(last_update_date__date=now),
            is_active=True,
            type_of_distribution__in=local_types,
        )

        settings.ROTATIONS_CONFIG_DIR.mkdir(exist_ok=True)

        with transaction.atomic():
            for distrib in rot_distributions:
                pack = distrib.get_next_pack()

                with open(
                    settings.ROTATIONS_CONFIG_DIR / distrib.local_filename,
                    "w",
                    encoding="utf-8",
                ) as file:
                    file.write(distrib.format_config(pack))

                distrib.last_update_date = now
                if pack.queue_number is not None:
                    distrib.last_queue_number = pack.queue_number

                distrib.save()
