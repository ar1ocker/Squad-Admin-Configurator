from rest_framework.authtoken.models import TokenProxy as OriginalTokenProxy


class TokenProxy(OriginalTokenProxy):
    class Meta:
        proxy = True
        verbose_name = "Токен"
        verbose_name_plural = "1. Токены"
