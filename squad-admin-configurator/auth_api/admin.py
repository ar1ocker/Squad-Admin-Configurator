from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy as OriginalTokenProxy

from .models import TokenProxy

TokenAdmin.raw_id_fields = ["user"]

admin.site.unregister(OriginalTokenProxy)
admin.site.register(TokenProxy, TokenAdmin)
