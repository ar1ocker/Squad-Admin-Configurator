from django.contrib import admin
from django.urls import include, path
from server_rotations_api.routers import router as server_rotations_api_router

urlpatterns = [
    path("v1/api/privileged/", include("api.urls", namespace="api")),
    path(
        "v1/api/rotations/",
        include(server_rotations_api_router.urls),
    ),
    path("adminactions/", include("adminactions.urls")),
    path("", admin.site.urls),
]
