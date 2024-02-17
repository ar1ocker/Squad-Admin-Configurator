from django.contrib import admin
from utils import textarea_form

from .models import RotationDistribution


@admin.register(RotationDistribution)
class RotationDistributionAdmin(admin.ModelAdmin):
    form = textarea_form(RotationDistribution, ["description"])
    fields = [
        "is_active",
        "title",
        "rotation",
        "description",
        "type_of_distribution",
        "local_filename",
        "url",
        "last_update_date",
        "last_queue_number",
    ]
    list_display = [
        "is_active",
        "title",
        "type_of_distribution",
        "last_queue_number",
        "last_update_date",
        "local_filename",
        "url",
    ]
    list_editable = ["is_active"]
    list_display_links = ["title"]
    list_filter = ["is_active", "type_of_distribution"]
    search_fields = ["title", "description"]
