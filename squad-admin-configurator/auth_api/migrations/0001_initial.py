# Generated by Django 4.2.7 on 2024-02-08 07:50

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authtoken', '0003_tokenproxy'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Токен',
                'verbose_name_plural': 'Токены',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authtoken.tokenproxy',),
        ),
    ]
