from django.apps import AppConfig


class ApiConfig(AppConfig):
    def ready(self):
        from . import signals
        signals.connect_signals()

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = '2. Конфигурация API'
