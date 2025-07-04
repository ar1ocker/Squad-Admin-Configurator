# Generated by Django 4.2.14 on 2025-06-08 19:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('server_admins', '0004_alter_permission_options_alter_privileged_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privileged',
            name='servers_roles',
        ),
        migrations.AlterField(
            model_name='serverprivileged',
            name='privileged',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_accesses', to='server_admins.privileged', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='serverprivileged',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='privileged_accesses', to='server_admins.server', verbose_name='Сервер'),
        ),
        migrations.CreateModel(
            name='ServerPrivilegedPack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('steam_ids', models.TextField(blank=True, help_text='Поддерживаются комментарии начинающиеся с символа #', verbose_name='Список steam id')),
                ('max_ids', models.PositiveIntegerField(help_text='0 если ограничений нет', verbose_name='Максимальное количество ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активирован')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('date_of_end', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания действия')),
                ('comment', models.CharField(blank=True, max_length=200, verbose_name='Комментарий')),
                ('moderators', models.ManyToManyField(related_name='moderated_packs', to=settings.AUTH_USER_MODEL, verbose_name='Модераторы')),
                ('roles', models.ManyToManyField(blank=True, to='server_admins.role', verbose_name='Роли')),
                ('servers', models.ManyToManyField(blank=True, related_name='privileged_accesses_packs', to='server_admins.server', verbose_name='Сервера')),
            ],
            options={
                'verbose_name': 'Список пользователей',
                'verbose_name_plural': '6. Списки пользователей',
            },
        ),
    ]
