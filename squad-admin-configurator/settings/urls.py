from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("v1/api/privileged/", include("api.urls", namespace="api")),
    path(
        "v1/api/rotations/",
        include("server_rotations_api.urls", namespace="rotations_api"),
    ),
    path("adminactions/", include("adminactions.urls")),
    path("", admin.site.urls),
]
