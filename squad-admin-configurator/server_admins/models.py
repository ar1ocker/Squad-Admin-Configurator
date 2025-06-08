import re
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from .steam_ids_parser import SteamIDsSpec

if TYPE_CHECKING:
    from django.db.models import Manager

User = get_user_model()


class Server(models.Model):
    """
    Модель хранения отдельного сервера, вариантом выбора раздачи этого файла
    """

    is_active = models.BooleanField("Активирован", default=True)

    title = models.CharField("Название", max_length=50)

    description = models.CharField("Описание", max_length=300, blank=True)

    privileged_accesses: "Manager[ServerPrivileged]"
    privileged_accesses_packs: "Manager[ServerPrivilegedPack]"

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Сервер"
        verbose_name_plural = "1. Сервера"
        ordering = ["-title"]


class Permission(models.Model):
    """
    Разрешения игрового сервера, поле title должно быть валидным
    игровых разрешением, например cameraman
    """

    title = models.CharField("Название", max_length=100, unique=True)
    description = models.CharField("Описание", max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Разрешение"
        verbose_name_plural = "4. Разрешения"


class Role(models.Model):
    """
    Роль объединяет в себе несколько разрешений и выдаётся определенным
    привилегированным пользователям
    """

    title = models.CharField("Название", max_length=200, unique=True)
    is_active = models.BooleanField("Активирован", default=True)
    permissions: "models.ManyToManyField[Permission, Permission]" = models.ManyToManyField(
        Permission, blank=True, verbose_name="Разрешения"
    )
    description = models.CharField("Описание", max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "3. Роли"


class Privileged(models.Model):
    """
    Привилегированный пользователь который добавляется в файлы конфигурации
    админов для игровых серверов
    """

    name = models.CharField("Имя", max_length=200)
    steam_id = models.BigIntegerField("Steam ID", unique=True)

    is_active = models.BooleanField("Активирован", default=True)
    description = models.TextField("Описание", blank=True)
    creation_date = models.DateTimeField("Дата добавления", auto_now_add=True)
    date_of_end = models.DateTimeField("Общая дата окончания полномочий", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "2. Пользователи"

    def clean(self) -> None:
        self.name = re.sub(r"\s", " ", self.name)


class ServerPrivileged(models.Model):
    """
    Промежуточная модель для хранения связи Privileged => Server с
    дополнительной информацией
    """

    server = models.ForeignKey(
        Server, verbose_name="Сервер", related_name="privileged_accesses", on_delete=models.CASCADE
    )
    privileged = models.ForeignKey(
        Privileged, verbose_name="Пользователь", related_name="server_accesses", on_delete=models.CASCADE
    )
    roles: "models.ManyToManyField[Role, Role]" = models.ManyToManyField(Role, verbose_name="Роль")

    is_active = models.BooleanField("Активирована", default=True)
    creation_date = models.DateTimeField("Дата добавления", auto_now_add=True)
    date_of_end = models.DateTimeField("Дата окончания роли", blank=True, null=True)

    comment = models.CharField("Комментарий", blank=True, max_length=200)

    def __str__(self) -> str:
        return f"ID {self.pk}"

    class Meta:
        verbose_name = "Роль на сервере"
        verbose_name_plural = "5. Роли пользователей на серверах"


class ServerPrivilegedPack(models.Model):
    title = models.CharField(verbose_name="Название", max_length=200)

    servers = models.ManyToManyField(
        Server, verbose_name="Сервера", related_name="privileged_accesses_packs", blank=True
    )

    steam_ids = models.TextField(
        verbose_name="Список steam id", blank=True, help_text="Поддерживаются комментарии начинающиеся с символа #"
    )
    roles: "models.ManyToManyField[Role, Role]" = models.ManyToManyField(Role, verbose_name="Роли", blank=True)
    max_ids = models.PositiveIntegerField(verbose_name="Максимальное количество ID", help_text="0 если ограничений нет")
    moderators = models.ManyToManyField(User, verbose_name="Модераторы", related_name="moderated_packs")

    is_active = models.BooleanField("Активирован", default=True)
    creation_date = models.DateTimeField("Дата добавления", auto_now_add=True)
    date_of_end = models.DateTimeField("Дата окончания действия", blank=True, null=True)

    comment = models.CharField("Комментарий", blank=True, max_length=200)

    def __str__(self) -> str:
        return f"ID {self.pk}"

    class Meta:
        verbose_name = "Список пользователей"
        verbose_name_plural = "6. Списки пользователей"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        if not self.is_active:
            return

        nodes = SteamIDsSpec.parse(self.steam_ids)
        errors = SteamIDsSpec.check_errors(nodes=nodes)

        if errors:
            raise ValidationError({"steam_ids": [", ".join(errors)]})

        steam_ids = list(filter(lambda node: node.kind == SteamIDsSpec.STEAMID.name, nodes))

        if self.max_ids > 0 and len(steam_ids) > self.max_ids:
            raise ValidationError({"steam_ids": [f"Максимальное количество ID - {self.max_ids}"]})
