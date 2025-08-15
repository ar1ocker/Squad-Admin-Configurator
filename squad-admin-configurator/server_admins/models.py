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

    is_active = models.BooleanField(
        "Активирован",
        help_text="Активирован ли сервер, если флаг не установлен - конфигурация этого сервера будет пустая",
        default=True,
    )

    title = models.CharField("Название", help_text="Название сервера", max_length=50)

    description = models.CharField("Описание", help_text="Описание сервера", max_length=300, blank=True)

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

    title = models.CharField(
        "Название",
        help_text="Название игрового разрешения из конфигурации Admins.cfg в Squad",
        max_length=100,
        unique=True,
    )
    description = models.CharField("Описание", help_text="Описание игрового разрешения", max_length=300, blank=True)

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

    title = models.CharField("Название", help_text="Название роли", max_length=200, unique=True)
    is_active = models.BooleanField(
        "Активирован",
        help_text="Активирована ли роль, если флаг не установлен - роль будет убрана из всех конфигураций",
        default=True,
    )
    permissions: "models.ManyToManyField[Permission, Permission]" = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="Разрешения",
        help_text="Набор разрешений который действует для этой роли",
    )
    description = models.CharField("Описание", help_text="Описание роли", max_length=300, blank=True)

    privileged_accesses: "Manager[ServerPrivileged]"

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

    name = models.CharField("Имя", help_text="Имя привилегированного пользователя", max_length=200)
    steam_id = models.BigIntegerField("Steam ID", help_text="Steam ID 64", unique=True)

    is_active = models.BooleanField(
        "Активирован",
        help_text="Активирован ли глобально пользователь, если флаг не установлен"
        " - пользователь будет убран из конфигурации",
        default=True,
    )
    description = models.TextField("Описание", help_text="Описание пользователя", blank=True)
    creation_date = models.DateTimeField(
        "Дата добавления", help_text="Дата добавления пользователя на сайт", auto_now_add=True
    )
    date_of_end = models.DateTimeField(
        "Общая дата окончания полномочий",
        help_text="Дата после которой флаг 'Активирован' будет автоматически выключен",
        blank=True,
        null=True,
    )

    server_accesses: "Manager[ServerPrivileged]"

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
        Server,
        verbose_name="Сервер",
        help_text="Сервер на котором выдана роль",
        related_name="privileged_accesses",
        on_delete=models.CASCADE,
    )
    privileged = models.ForeignKey(
        Privileged,
        verbose_name="Пользователь",
        help_text="Привилегированный пользователь которому выдана роль(и) на сервере",
        related_name="server_accesses",
        on_delete=models.CASCADE,
    )
    roles: "models.ManyToManyField[Role, Role]" = models.ManyToManyField(
        Role, verbose_name="Роль", help_text="Список ролей", related_name="privileged_accesses"
    )

    is_active = models.BooleanField(
        "Активирована",
        help_text="Активирована ли данная роль на сервере, если не флаг не установлен - "
        "данная роль на сервере будет убрана из конфигурации",
        default=True,
    )
    creation_date = models.DateTimeField(
        "Дата добавления", help_text="Дата добавления роли на сервере", auto_now_add=True
    )
    date_of_end = models.DateTimeField(
        "Дата окончания роли",
        help_text="Дата после которой флаг 'Активирован' будет автоматически выключен",
        blank=True,
        null=True,
    )

    comment = models.CharField("Комментарий", blank=True, max_length=200)

    def __str__(self) -> str:
        return f"ID {self.pk}"

    class Meta:
        verbose_name = "Роль на сервере"
        verbose_name_plural = "5. Роли пользователей на серверах"


class ServerPrivilegedPack(models.Model):
    title = models.CharField(
        verbose_name="Название", help_text="Название списка привилегированных пользователей", max_length=200
    )

    servers = models.ManyToManyField(
        Server,
        verbose_name="Сервера",
        help_text="Список серверов на которых будут действовать роли",
        related_name="privileged_accesses_packs",
        blank=True,
    )

    steam_ids = models.TextField(
        verbose_name="Список Steam ID",
        blank=True,
        help_text="Список Steam ID через пробел или с новой строки. "
        "Поддерживаются комментарии начинающиеся с символа #",
    )
    roles: "models.ManyToManyField[Role, Role]" = models.ManyToManyField(
        Role, verbose_name="Роли", help_text="Список ролей которые будут действовать на серверах", blank=True
    )
    max_ids = models.PositiveIntegerField(
        verbose_name="Максимальное количество ID",
        help_text="Максимальное разрешенное количество SteamID которое можно записать в список. "
        "0 если ограничений нет",
        default=0,
    )
    moderators = models.ManyToManyField(
        User,
        verbose_name="Модераторы",
        related_name="moderated_packs",
        help_text="Модераторы которые могут изменять список",
        blank=True,
    )

    is_active = models.BooleanField(
        "Активирован",
        help_text="Активирован ли этот список, если не установлено - список Steam ID будет убран из конфигурации",
        default=True,
    )
    creation_date = models.DateTimeField(
        "Дата добавления", help_text="Дата добавления списка на сайт", auto_now_add=True
    )
    date_of_end = models.DateTimeField(
        "Дата окончания действия",
        help_text="Дата после которой флаг 'Активирован' будет автоматически выключен",
        blank=True,
        null=True,
    )

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
            raise ValidationError({"steam_ids": errors})

        steam_ids = list(filter(lambda node: node.kind == SteamIDsSpec.STEAMID.name, nodes))

        if self.max_ids > 0 and len(steam_ids) > self.max_ids:
            raise ValidationError({"steam_ids": [f"Максимальное количество ID - {self.max_ids}"]})
