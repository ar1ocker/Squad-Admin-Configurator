from django.apps import AppConfig


class ServerAdminsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server_admins'
    verbose_name = 'Привилегированные пользователи и роли'
