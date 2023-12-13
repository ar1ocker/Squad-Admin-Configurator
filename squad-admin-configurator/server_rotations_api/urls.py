from django.urls import path

from .views import GetCurrentRotationConfig, GetNextRotationConfig

app_name = "server_rotations_api"

urlpatterns = [
    path(
        "<url>/current/",
        GetCurrentRotationConfig.as_view(),
        name="current_rotation_config",
    ),
    path(
        "<url>/next/",
        GetNextRotationConfig.as_view(),
        name="next_rotation_config",
    ),
]
