from django.apps import AppConfig


class ServerAdminsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "server_admins"
    verbose_name = "1. Привилегированные пользователи"

    def ready(self):
        import server_admins.access  # noqa
