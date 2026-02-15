from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
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
        "current_rotation_url",
        "local_filename",
    ]
    list_editable = ["is_active"]
    list_display_links = ["title"]
    list_filter = ["is_active", "type_of_distribution"]
    search_fields = ["title", "description"]

    @admin.display(description="Ссылка текущую ротацию", ordering="url")
    def current_rotation_url(self, obj: RotationDistribution):
        if obj.url:
            return format_html(
                '<a href="{0}" target="_blank">{0}</a>',
                reverse("rotation_distribution-current", args=(obj.url,)),
            )
