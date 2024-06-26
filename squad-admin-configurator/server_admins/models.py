import re

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Server(models.Model):
    """
    Модель хранения отдельного сервера, вариантом выбора раздачи этого файла
    """

    is_active = models.BooleanField("Активирован", default=True)

    title = models.CharField("Название", max_length=50)

    description = models.CharField("Описание", max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Сервер"
        verbose_name_plural = "1. Сервера"
        ordering = ["-title"]

    def get_config(self) -> str:
        time_format: str = settings.TIME_FORMAT
        now: timezone.datetime = timezone.now()

        if not self.is_active:
            return f"// {self.title} DISABLED! {now.strftime(time_format)}"

        config_text: str = f"// {self.title} {now.strftime(time_format)}\n\n"

        server_roles = (
            ServerPrivileged.objects.filter(
                Q(date_of_end__gte=now) | Q(date_of_end=None),
                Q(privileged__date_of_end__gte=now) | Q(privileged__date_of_end=None),
                privileged__is_active=True,
                is_active=True,
                server=self,
            )
            .select_related("privileged")
            .prefetch_related("roles__permissions")
        )

        roles: dict = {}
        privileged_by_role: dict = {}

        for server_role in server_roles:
            for role in server_role.roles.all():
                if not role.is_active:
                    continue

                if role.title not in roles:
                    permissions: str = ",".join([perm.title for perm in role.permissions.all()])
                    roles[role.title] = f"Group={role.title}:{permissions}"
                    privileged_by_role[role.title] = f"// {role.title}\n"

                privileged_by_role[role.title] += (
                    f"Admin={server_role.privileged.steam_id}"
                    f":{role.title}"
                    " //"
                    f" {server_role.privileged.name}"
                    "\n"
                )

        roles_text: str = "\n".join([role for role in roles.values()])
        privileged_text: str = "\n\n".join([text for text in privileged_by_role.values()])
        config_text += f"// Roles\n{roles_text}\n\n{privileged_text}"

        return config_text


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
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="Разрешения")
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

    servers_roles = models.ManyToManyField(Server, through="ServerPrivileged", blank=True, verbose_name="Сервера")

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

    server = models.ForeignKey(Server, verbose_name="Сервер", on_delete=models.CASCADE)
    privileged = models.ForeignKey(Privileged, verbose_name="Пользователь", on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, verbose_name="Роль")

    is_active = models.BooleanField("Активирована", default=True)
    creation_date = models.DateTimeField("Дата добавления", auto_now_add=True)
    date_of_end = models.DateTimeField("Дата окончания роли", blank=True, null=True)

    comment = models.CharField("Комментарий", blank=True, max_length=200)

    def __str__(self) -> str:
        return f"ID {self.id}"

    class Meta:
        verbose_name = "Роль на сервере"
        verbose_name_plural = "5. Роли пользователей на серверах"
