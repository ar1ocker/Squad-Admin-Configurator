from django.conf import settings

from .models import AdminsConfigDistribution


def create_local_configs() -> None:
    """
    Генерация локальных конфигов администраторов
    для всех необходимых серверов
    """
    distributions = AdminsConfigDistribution.objects.filter(
        type_of_distribution__in=AdminsConfigDistribution.TYPES_OF_DISTRIBUTION_WITH_LOCAL  # noqa: E501
    )

    for distribution in distributions:
        if distribution.is_active:
            create_local_config(distribution)


def create_local_config(distrib: AdminsConfigDistribution) -> None:
    """
    Генерация локального конфига администраторов
    для отдельного игрового сервера
    """
    if distrib.type_of_distribution not in AdminsConfigDistribution.TYPES_OF_DISTRIBUTION_WITH_LOCAL:
        return

    settings.ADMINS_CONFIG_DIR.mkdir(exist_ok=True)

    with open(
        settings.ADMINS_CONFIG_DIR / distrib.local_filename,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(distrib.server.get_config())
