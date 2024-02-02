from django.db.models.signals import post_save
from server_admins.models import Server

from .models import AdminsConfigDistribution


def connect_signals():
    """Подключает сигналы на старте приложения"""
    post_save.connect(remove_when_distribution_changed, sender=Server)


def remove_when_distribution_changed(sender, instance, **kwargs):
    """
    Удаление ServerUrl связанного с Server, когда последний больше
    недоступен для раздачи по API
    """
    server = instance

    if (
        server.type_of_distribution
        not in Server.TYPES_OF_DISTRIBUTION_WITH_API
    ):
        try:
            AdminsConfigDistribution.objects.get(server=server).delete()
        except AdminsConfigDistribution.DoesNotExist:
            pass
