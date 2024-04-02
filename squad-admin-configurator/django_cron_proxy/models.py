from django_cron.models import CronJobLog as OriginalCronJobLog


class CronJobLog(OriginalCronJobLog):
    class Meta:
        proxy = True
        verbose_name = "Лог"
        verbose_name_plural = "1. Логи"
