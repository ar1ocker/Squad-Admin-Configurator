from django.core.exceptions import ValidationError
from django.db import models

from .layers_parser import LayerSpec


class LayersPack(models.Model):
    """Пак с картами"""

    title = models.CharField("Название", help_text="Название всего набора с картами", max_length=100, unique=True)
    description = models.CharField("Описание", help_text="Описание набора", max_length=255, blank=True)
    layers = models.TextField(
        "Список карт",
        help_text="Список карт, каждая карта (леер) с новой строки, поддерживаются комментарии с символа # или //",
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
    """Through модель между наборами и ротациями"""

    pack = models.ForeignKey(
        LayersPack, on_delete=models.CASCADE, verbose_name="Набор с картами", help_text="Набор с картами"
    )
    slug = models.SlugField(
        "Название для url или файла",
        help_text="Название для url или файла",
        max_length=255,
        null=True,
        blank=True,
    )
    description = models.CharField(
        "Описание", help_text="Описание набора с картами именно в этой ротации", max_length=255, blank=True, null=True
    )
    rotation = models.ForeignKey(
        "Rotation", on_delete=models.CASCADE, related_name="packs_through", verbose_name="ротация", help_text="Ротация"
    )

    queue_number = models.PositiveSmallIntegerField(
        "Номер в очереди",
        help_text="Он лишь отражает очередность в списке и ему совсем не обязательно идти подряд )",
        null=True,
        blank=True,
    )

    start_time_at = models.TimeField(
        "Время начала применения набора карт",
        null=True,
        blank=True,
        help_text="Дата и время в которое будет отправляться данный набор карт",
    )

    end_time_at = models.TimeField(
        "Время окончания применения набора карт",
        null=True,
        blank=True,
        help_text="Дата и время когда в которое заканчивает отправляться данный набор карт",
    )

    start_date = models.DateField(
        "Дата применения набора карт",
        null=True,
        blank=True,
        help_text="При выставлении этой даты - номер в очереди сбрасывается",
    )

    class Meta:
        verbose_name = "набор с картами"
        verbose_name_plural = "наборы с картами"
        constraints = [
            models.UniqueConstraint(
                condition=models.Q(slug__isnull=False),
                fields=["slug", "rotation"],
                name="rotation_layers_pack_unique_slug_and_rotation_when_slug_isnull_false",
            ),
        ]

    def __str__(self) -> str:
        return "Набор с картами"

    def clean(self) -> None:
        super().clean()

        if (
            self.slug
            and self.__class__.objects.filter(slug=self.slug, rotation_id=self.rotation_id).exclude(pk=self.pk).exists()
        ):
            raise ValidationError({"slug": ["Такое название уже есть"]})

        if self.start_date and (self.start_time_at is None or self.end_time_at is None):
            raise ValidationError(
                {
                    "__all__": ["Если задана дата применения набора карт - должно быть задано и время"],
                    "start_time_at": ["Задайте время начала"],
                    "end_time_at": ["Задайте дату окончания"],
                }
            )

        if self.start_time_at and self.end_time_at:
            if self.start_time_at > self.end_time_at:
                raise ValidationError(
                    {
                        "start_time_at": ["Дата начала больше даты окончания"],
                        "end_time_at": ["Дата начала больше даты окончания"],
                    }
                )
            self.queue_number = None
        elif self.queue_number is None:
            raise ValidationError(
                {
                    "start_time_at": ["Задайте время начала и окончания или номер в очереди"],
                    "end_time_at": ["Задайте время начала и окончания или номер в очереди"],
                    "queue_number": ["Задайте время начала и окончания или номер в очереди"],
                }
            )


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
