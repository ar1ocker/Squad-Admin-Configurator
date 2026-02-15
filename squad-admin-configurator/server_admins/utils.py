from datetime import datetime

from django.conf import settings


def date_or_perpetual(date: datetime, date_format=settings.DATETIME_FORMAT):
    return date.strftime(date_format) if date else "∞"
