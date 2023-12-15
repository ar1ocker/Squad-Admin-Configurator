from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F


class GameMode(models.Model):
    """Хранение названия игрового режима"""

    name = models.CharField("Краткое название", max_length=50)
    description = models.CharField("Описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "игровой режим"
        verbose_name_plural = "5. Игровые режимы"

    def __str__(self):
        return self.name


class Team(models.Model):
    """Названия команд"""

    abbreviation = models.CharField("Аббревиатура", max_length=50)
    name = models.CharField("Полное название", max_length=255, blank=True)
    description = models.CharField("Описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "команда"
        verbose_name_plural = "4. Команды"
        ordering = ["-abbreviation"]

    def __str__(self):
        return self.name


class Layer(models.Model):
    name = models.CharField("Название карты", max_length=255, unique=True)
    team1 = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Команда 1",
        related_name="layer_team1",
    )
    team2 = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Команда 2",
        related_name="layer_team2",
    )
    game_mode = models.ForeignKey(
        GameMode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Игровой режим",
    )
    description = models.CharField("Описание", max_length=511, blank=True)

    class Meta:
        verbose_name = "карта"
        verbose_name_plural = "3. Карты"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class LayerPackLayer(models.Model):
    layer = models.ForeignKey(
        Layer, verbose_name="карта", on_delete=models.CASCADE
    )
    pack = models.ForeignKey(
        "LayersPack",
        verbose_name="пак",
        related_name="layers_through",
        on_delete=models.CASCADE,
    )
    queue_number = models.PositiveSmallIntegerField("Номер в очереди")

    class Meta:
        verbose_name = "карта в паке"
        verbose_name_plural = "карты в паке"
        ordering = ["queue_number"]

    def __str__(self):
        return f"#{self.queue_number}"


class LayersPack(models.Model):
    """Пак с картами"""

    is_active = models.BooleanField("Активирован", default=True)
    title = models.CharField("Название", max_length=100, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    layers = models.ManyToManyField(
        Layer, through="LayerPackLayer", verbose_name="Список карт"
    )
    creation_date = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "пак с картами"
        verbose_name_plural = "2. Паки с картами"
        ordering = ["-creation_date"]

    def __str__(self) -> str:
        status = "🟢 " if self.is_active else "🔴 "
        return status + self.title

    def get_list_layers(self):
        return "\n".join(
            (through.layer.name for through in self.layers_through.all())
        )


class RotationLayersPack(models.Model):
    """Through модель между паками и ротациями"""

    pack = models.ForeignKey(
        LayersPack, on_delete=models.CASCADE, verbose_name="пак с картами"
    )
    description = models.CharField(
        "Описание", max_length=255, blank=True, null=True
    )
    rotation = models.ForeignKey(
        "Rotation",
        on_delete=models.CASCADE,
        related_name="packs_through",
        verbose_name="ротация",
    )
    queue_number = models.PositiveSmallIntegerField(
        "Номер в очереди", null=True, blank=True
    )
    start_date = models.DateField(
        "Дата применения ротации",
        null=True,
        blank=True,
        help_text="При выставлении этой даты - номер в очереди сбрасывается",
    )

    class Meta:
        ordering = [F("queue_number").asc(nulls_first=True), "start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["rotation", "start_date"],
                condition=models.Q(start_date__isnull=False),
                name="rotation_start_date_unique",
                violation_error_message="Дата начала должна быть уникальной",
            ),
        ]
        verbose_name = "пак с картами"
        verbose_name_plural = "паки с картами"

    def __str__(self) -> str:
        if self.queue_number is not None:
            return f"#{self.queue_number}"
        else:
            return str(self.start_date.strftime(settings.TIME_FORMAT))

    def clean(self):
        if self.start_date is None and self.queue_number is None:
            raise ValidationError(
                {
                    "start_date": "Задайте дату начала или номер в очереди",
                    "queue_number": "Задайте дату начала или номер в очереди",
                }
            )
        if self.start_date:
            self.queue_number = None

        super().clean()


class Rotation(models.Model):
    title = models.CharField("Название", max_length=50, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True)

    packs = models.ManyToManyField(
        LayersPack, verbose_name="Наборы карт", through=RotationLayersPack
    )
    creation_date = models.DateTimeField("Дата добавление", auto_now_add=True)

    class Meta:
        verbose_name = "ротация"
        verbose_name_plural = "1. Ротации"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title
