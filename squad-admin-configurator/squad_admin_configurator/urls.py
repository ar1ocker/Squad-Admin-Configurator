from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api'))
]
