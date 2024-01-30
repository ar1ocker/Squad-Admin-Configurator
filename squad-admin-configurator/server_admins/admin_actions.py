from django.conf import settings

from .models import Server

ADMINS_CONFIG_DIR = settings.ADMINS_CONFIG_DIR


def create_local_configs():
    """
    Генерация локальных конфигов администраторов
    для всех необходимых серверов
    """
    servers = Server.objects.filter(
        type_of_distribution__in=Server.TYPES_OF_DISTRIBUTION_WITH_LOCAL
    )

    for server in servers:
        create_local_config(server)


def create_local_config(server):
    """
    Генерация локального конфига администраторов
    для отдельного игрового сервера
    """
    if (
        server.type_of_distribution
        not in Server.TYPES_OF_DISTRIBUTION_WITH_LOCAL
    ):
        return

    ADMINS_CONFIG_DIR.mkdir(exist_ok=True)

    with open(
        ADMINS_CONFIG_DIR / server.local_filename, "w", encoding="utf-8"
    ) as file:
        file.write(server.get_config())
