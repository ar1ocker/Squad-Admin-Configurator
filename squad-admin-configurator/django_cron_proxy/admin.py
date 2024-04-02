from django.contrib import admin
from django_cron.admin import CronJobLogAdmin
from django_cron.models import CronJobLock as OriginalCronJobLock
from django_cron.models import CronJobLog as OriginalCronJobLog

from .models import CronJobLog

admin.site.unregister(OriginalCronJobLog)
admin.site.unregister(OriginalCronJobLock)

admin.site.register(CronJobLog, CronJobLogAdmin)
