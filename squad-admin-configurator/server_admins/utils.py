from django.conf import settings


def date_or_perpetual(date, date_format=settings.TIME_FORMAT):
    return date.strftime(date_format) if date else "∞"
