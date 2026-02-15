from base import DistributionModel
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from server_rotations.layers_parser import LayerSpec
from server_rotations.models import Rotation, RotationLayersPack


class RotationDistribution(DistributionModel):
    rotation = models.OneToOneField(
        Rotation,
        on_delete=models.CASCADE,
        verbose_name="Ротация",
        help_text="Ротация из которой будет ежедневно браться новые карты",
        related_name="distributions",
    )
    last_update_date = models.DateTimeField(
        "Дата последнего обновления",
        help_text="Дата когда в последний раз изменялся номер в очереди",
        blank=True,
        null=True,
    )
    last_queue_number = models.PositiveSmallIntegerField(
        "Последний номер в очереди", help_text="Последний номер набора с картами который был взят из ротации", default=1
    )

    class Meta(DistributionModel.Meta):
        verbose_name = "распространение ротации"
        verbose_name_plural = "1. Распространение ротаций"
        ordering = ["rotation"]

    def get_next_pack_by_queue(self) -> RotationLayersPack | None:
        rotation_pack_manager = RotationLayersPack.objects.select_related("pack")

        pack_m2m = (
            rotation_pack_manager.order_by(
                "queue_number",
            )
            .filter(
                queue_number__isnull=False,
                queue_number__gt=self.last_queue_number,
                rotation=self.rotation,
            )
            .first()
        )

        if pack_m2m is None:
            pack_m2m = (
                rotation_pack_manager.order_by("queue_number")
                .filter(
                    queue_number__isnull=False,
                    rotation=self.rotation,
                    start_date__isnull=True,
                )
                .first()
            )

        return pack_m2m

    def get_current_pack(self) -> RotationLayersPack | None:
        now: timezone.datetime = timezone.localtime()
        pack_m2m = (
            RotationLayersPack.objects.select_related("pack")
            .order_by(
                F("queue_number").asc(nulls_first=True),
                F("start_date").desc(nulls_first=False),
                "-start_time_at",
                "-end_time_at",
                "id",
            )
            .filter(
                Q(queue_number=self.last_queue_number)
                | Q(Q(start_date=now.date()) & Q(start_time_at__lte=now.time()) & Q(end_time_at__gte=now.time()))
                | Q(Q(start_date__isnull=True) & Q(start_time_at__lte=now.time()) & Q(end_time_at__gte=now.time())),
                rotation=self.rotation,
            )
            .first()
        )
        return pack_m2m

    def format_config(self, pack_m2m: RotationLayersPack | None) -> str:
        now = timezone.localtime()
        if pack_m2m is None:
            return f"// Ротаций не найдено {now.strftime(settings.DATETIME_FORMAT)} {settings.TIME_ZONE}"

        number = None
        date = None
        if pack_m2m.queue_number is not None:
            number = str(pack_m2m.queue_number)
        else:
            date = (
                f"{pack_m2m.start_date.strftime(settings.DATE_FORMAT) if pack_m2m.start_date else ""} "
                f"с {pack_m2m.start_time_at.strftime(settings.TIME_FORMAT)} "
                f"по {pack_m2m.end_time_at.strftime(settings.TIME_FORMAT)}"
            )

        layers = [layer.value for layer in LayerSpec.parse(pack_m2m.pack.layers) if layer.kind == LayerSpec.LAYER.name]

        layers_text = "\n".join(layers)

        config = (
            f"// {self.rotation.title}"
            f" - {number or date}"
            f" - {now.strftime(settings.DATETIME_FORMAT)} {settings.TIME_ZONE}\n\n"
            f"{layers_text}"
        )

        return config
