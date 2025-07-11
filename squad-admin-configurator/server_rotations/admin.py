from admin_ordering.admin import OrderableAdmin
from django.contrib import admin
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import BaseInlineFormSet, ValidationError
from utils import textarea_form

from .models import LayersPack, Rotation, RotationLayersPack


class RotationLayersPackFormset(BaseInlineFormSet):
    def clean(self):
        """
        Руками проверяем уникальность start_date, т.к. если задать в
        модели Meta.constraints UniqueConstraint с condition, то это поле
        не будет автоматически проверяться в formset
        """
        error = False
        error_message = None

        # Получаем "родные" ошибки
        try:
            super().clean()
        except ValidationError as e:
            error = True
            error_message = e.message_dict

        # Валидные формы которые не будут удаляться
        valid_forms = [form for form in self.forms if form.is_valid() and form not in self.deleted_forms]

        seen_data = set()
        for form in valid_forms:
            start_date = form.instance.start_date
            if start_date is None:
                continue

            if start_date not in seen_data:
                seen_data.add(start_date)
                continue

            form._errors[NON_FIELD_ERRORS] = self.error_class(
                ["Дата применения ротации должна быть уникальной"],
                renderer=self.renderer,
            )
            error = True

        if error:
            raise ValidationError(error_message or ["Ошибка при задании даты применения ротации"])


class RotationLayersPackInline(OrderableAdmin, admin.TabularInline):
    formset = RotationLayersPackFormset
    fields = [("queue_number", "start_date"), "pack", "description"]
    model = RotationLayersPack
    extra = 0
    ordering_field = "queue_number"


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
    fields = ["title", "layers", "description", "creation_date"]
    readonly_fields = ["creation_date"]
    list_display = ["title", "creation_date"]
    list_display_links = ["title", "creation_date"]
    list_filter = ["creation_date"]
    search_fields = ["title", "description"]
