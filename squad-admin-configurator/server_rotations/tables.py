import django_tables2


class LayersTable(django_tables2.Table):
    id = django_tables2.TemplateColumn(verbose_name="#", template_code="{{ row_counter }}")
    layer = django_tables2.Column(verbose_name="Название карты")
