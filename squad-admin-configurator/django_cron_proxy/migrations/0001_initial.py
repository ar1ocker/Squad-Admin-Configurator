# Generated by Django 4.2.11 on 2024-04-01 14:52

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("django_cron", "0003_cronjoblock"),
    ]

    operations = [
        migrations.CreateModel(
            name="CronJobLog",
            fields=[],
            options={
                "verbose_name": "Лог",
                "verbose_name_plural": "1. Логи",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_cron.cronjoblog",),
        ),
    ]