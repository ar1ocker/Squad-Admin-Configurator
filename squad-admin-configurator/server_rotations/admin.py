from django.contrib import admin
from django.db.models.query import F, QuerySet
from django.http.request import HttpRequest
from django.utils.safestring import SafeText
from utils import textarea_form

from .layers_parser import LayerSpec
from .models import LayersPack, Rotation, RotationLayersPack
from .tables import LayersTable


class RotationLayersPackInline(admin.StackedInline):
    fields = ["queue_number", "pack", "start_time_at", "end_time_at", "start_date", "slug", "description"]
    model = RotationLayersPack
    extra = 0
    ordering = [F("queue_number").asc(nulls_first=True), F("start_date").desc(nulls_first=False), "id"]


@admin.register(Rotation)
class RotationAdmin(admin.ModelAdmin):
    form = textarea_form(Rotation, ["description"])
    inlines = [RotationLayersPackInline]
    fields = ["title", "description", "creation_date"]
    readonly_fields = ["creation_date"]
    list_display = ["title", "creation_date"]
    list_display_links = ["title", "creation_date"]
    list_filter = ["creation_date"]
    search_fields = ["title", "description"]


@admin.register(LayersPack)
class LayersPackAdmin(admin.ModelAdmin):
    form = textarea_form(LayersPack, ["description"])
    fields = ["title", "parsed_layers", "layers", "description", "creation_date"]
    readonly_fields = ["creation_date", "parsed_layers"]
    list_display = ["title", "creation_date"]
    list_display_links = ["title", "creation_date"]
    list_filter = ["creation_date"]
    search_fields = ["title", "description"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        self.request = request
        return super().get_queryset(request)

    @admin.display(description="Обработанный список карт")
    def parsed_layers(self, obj: LayersPack) -> str | SafeText:
        if obj.layers == "":
            return "-"

        layers = [{"layer": node.value} for node in LayerSpec.parse(obj.layers) if node.kind == LayerSpec.LAYER.name]

        if len(layers) == 0:
            return "-"

        table = LayersTable(layers, orderable=False)

        return table.as_html(self.request)
