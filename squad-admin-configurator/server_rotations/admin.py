from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from utils import textarea_form

from .models import (
    GameMode,
    Layer,
    LayerPackLayer,
    LayersPack,
    Rotation,
    RotationLayersPack,
    Team,
)


class RotationLayersPackInline(OrderableAdmin, admin.TabularInline):
    fields = [("queue_number", "start_date"), "pack", "description"]
    model = RotationLayersPack
    extra = 0
    ordering_field = "queue_number"
    autocomplete_fields = ["pack"]


class LayerPackLayerInline(OrderableAdmin, admin.TabularInline):
    fields = ["queue_number", "layer"]
    model = LayerPackLayer
    extra = 0
    ordering_field = "queue_number"
    autocomplete_fields = ["layer"]


@admin.register(GameMode)
class GameModeAdmin(admin.ModelAdmin):
    form = textarea_form(GameMode, ["description"])
    fields = ["name", "description"]
    list_display = fields
    list_display_links = fields
    search_fields = fields


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = textarea_form(Team, ["description"])
    fields = ["abbreviation", "name", "description"]
    list_display = [
        "abbreviation",
        "name",
    ]
    list_display_links = [
        "abbreviation",
        "name",
    ]
    search_fields = fields


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    form = textarea_form(Layer, ["description"])
    fields = ["name", "team1", "team2", "game_mode", "description"]
    list_display = ["name", "team1", "team2", "game_mode"]
    list_display_links = ["name", "team1", "team2", "game_mode"]
    search_fields = [
        "name",
        "description",
        "game_mode__name",
        "team1__abbreviation",
        "team2__abbreviation",
    ]
    list_filter = ["game_mode", "team1", "team2"]
    autocomplete_fields = ["game_mode", "team1", "team2"]


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
    inlines = [LayerPackLayerInline]
    form = textarea_form(LayersPack, ["description"])
    fields = ["is_active", "title", "description", "creation_date"]
    readonly_fields = ["creation_date"]
    list_display = ["is_active", "title", "creation_date"]
    filter_horizontal = ["layers"]
    list_editable = ["is_active"]
    list_display_links = ["title", "creation_date"]
    list_filter = ["is_active", "creation_date"]
    search_fields = ["title", "description"]
