import django_tables2


class SteamIDSTable(django_tables2.Table):
    id = django_tables2.TemplateColumn(verbose_name="#", template_code="{{ row_counter }}")
    steam_id = django_tables2.TemplateColumn(
        verbose_name="Steam ID",
        template_code='<a href="https://steamcommunity.com/profiles/{{ value }}" target="_blank">{{ value }}</a>',
    )
    comment = django_tables2.Column(verbose_name="Комментарий")
