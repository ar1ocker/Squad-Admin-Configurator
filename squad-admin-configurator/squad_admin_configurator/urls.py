from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path("v1/api/privileged/", include("api.urls", namespace="api")),
    path(
        "v1/api/rotations/",
        include("server_rotations_api.urls", namespace="rotations_api"),
    ),
    path("adminactions/", include("adminactions.urls")),
    path("jet/", include("jet.urls", "jet")),
    path("", admin.site.urls),
]
