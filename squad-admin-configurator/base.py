import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


def filename_validator(value):
    if value is not None and not re.fullmatch(
        r"^(?!.*[_-][_-])[A-Za-z0-9_]+$", value
    ):
        raise ValidationError(
            "Только латинские буквы, цифры и знак подчеркивания, множественные"
            " знаки подчеркивания запрещены"
        )


def url_postfix_validator(value):
    if value is not None and not re.fullmatch("[A-Za-z0-9_]+", value):
        raise ValidationError(
            "Только латинские буквы, цифры и знак подчеркивания"
        )


class DistributionModel(models.Model):
    LOCAL = "LOCAL"
    API = "API"
    API_AND_LOCAL = "API_LOCAL"

    TYPES_OF_DISTRIBUTION = [
        (LOCAL, "Локальный файл"),
        (API, "Через API"),
        (API_AND_LOCAL, "Локальный файл и API"),
    ]

    TYPES_OF_DISTRIBUTION_WITH_API = [API, API_AND_LOCAL]

    TYPES_OF_DISTRIBUTION_WITH_LOCAL = [LOCAL, API_AND_LOCAL]

    is_active = models.BooleanField("Активирован", default=True)

    title = models.CharField("Название", max_length=50, unique=True)

    description = models.CharField("Описание", max_length=300, blank=True)

    type_of_distribution = models.CharField(
        "Вариант распространения конфигурации",
        choices=TYPES_OF_DISTRIBUTION,
        max_length=10,
        default=LOCAL,
    )

    local_filename = models.CharField(
        "Название локального файла",
        max_length=100,
        blank=True,
        null=True,
        validators=[filename_validator],
    )
    url = models.CharField(
        "Постфикс url",
        max_length=100,
        blank=True,
        null=True,
        validators=[url_postfix_validator],
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["local_filename"],
                condition=Q(local_filename__isnull=False),
                name="distribution_local_filename_unique",
                violation_error_message=(
                    "Название локального файла должно быть уникальным"
                ),
            ),
            models.UniqueConstraint(
                fields=["url"],
                condition=Q(url__isnull=False),
                name="distribution_url_unique",
                violation_error_message="Постфикс url должен быть уникальным",
            ),
        ]

    def clean(self):
        errors = {}
        if (
            self.type_of_distribution in self.TYPES_OF_DISTRIBUTION_WITH_API
            and not self.url
        ):
            errors["url"] = "Введите url"

        if (
            self.type_of_distribution in self.TYPES_OF_DISTRIBUTION_WITH_LOCAL
            and not self.local_filename
        ):
            errors["local_filename"] = "Введите имя файла"

        if errors:
            raise ValidationError(errors)

        if (
            self.type_of_distribution
            not in self.TYPES_OF_DISTRIBUTION_WITH_API
        ):
            self.url = None

        if (
            self.type_of_distribution
            not in self.TYPES_OF_DISTRIBUTION_WITH_LOCAL
        ):
            self.local_filename = None
