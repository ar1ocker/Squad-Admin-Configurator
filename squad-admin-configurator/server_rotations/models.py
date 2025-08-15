from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F

from .layers_parser import LayerSpec


class LayersPack(models.Model):
    """Пак с картами"""

    title = models.CharField("Название", help_text="Название всего пака с картами", max_length=100, unique=True)
    description = models.CharField("Описание", help_text="Описание пака", max_length=255, blank=True)
    layers = models.TextField(
        "Список карт",
        help_text="Список карт, каждая карта (леер) с новой строки, поддерживаются комментарии с символа #",
        blank=True,
    )
    creation_date = models.DateTimeField(
        "Дата добавления", help_text="Дата добавления наборка с картами", auto_now_add=True
    )

    class Meta:
        verbose_name = "набор с картами"
        verbose_name_plural = "2. Наборы с картами"
        ordering = ["-creation_date"]

    def __str__(self) -> str:
        return self.title

    def clean(self):
        parsed_layers = LayerSpec.parse(self.layers)

        errors: list[str] = LayerSpec.check_errors(parsed_layers)

        if errors:
            raise ValidationError({"layers": errors})


class RotationLayersPack(models.Model):
    """Through модель между паками и ротациями"""

    pack = models.ForeignKey(
        LayersPack, on_delete=models.CASCADE, verbose_name="Набор с картами", help_text="Набор с картами"
    )
    description = models.CharField(
        "Описание", help_text="Описание набора с картами именно в этой ротации", max_length=255, blank=True, null=True
    )
    rotation = models.ForeignKey(
        "Rotation", on_delete=models.CASCADE, related_name="packs_through", verbose_name="ротация", help_text="Ротация"
    )

    queue_number = models.PositiveSmallIntegerField(
        "Номер в очереди",
        help_text="Он лишь отражает очередность в списке и совсем не ему не обязательно идти подряд )",
        null=True,
        blank=True,
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
        verbose_name = "набор с картами"
        verbose_name_plural = "наборы с картами"

    def __str__(self) -> str:
        if self.queue_number is not None:
            return f"#{self.queue_number}"
        elif self.start_date is not None:
            return str(self.start_date.strftime(settings.TIME_FORMAT))
        else:
            return "Набор с картами"

    def clean(self):
        if self.start_date is None and self.queue_number is None:
            raise ValidationError(
                {
                    "start_date": ["Задайте дату начала или номер в очереди"],
                    "queue_number": ["Задайте дату начала или номер в очереди"],
                }
            )
        if self.start_date:
            self.queue_number = None

        super().clean()


class Rotation(models.Model):
    title = models.CharField("Название", help_text="Название ротации (до 50 символов)", max_length=50, unique=True)
    description = models.CharField("Описание", help_text="Описание ротации", max_length=255, blank=True)

    packs = models.ManyToManyField(
        LayersPack, verbose_name="Наборы карт", help_text="Список наборов карт по порядку", through=RotationLayersPack
    )

    creation_date = models.DateTimeField("Дата добавление", help_text="Дата добавления ротации", auto_now_add=True)

    class Meta:
        verbose_name = "ротация"
        verbose_name_plural = "1. Ротации"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title
