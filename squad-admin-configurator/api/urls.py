from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    PermissionViewSet,
    PrivilegedViewSet,
    RoleViewSet,
    RoleWebhookView,
    ServerConfigView,
    ServerPrivilegedViewSet,
    ServerViewSet,
)

app_name = "api"

router = SimpleRouter()

router.register("servers", ServerViewSet)
router.register("permissions", PermissionViewSet)
router.register("roles", RoleViewSet)
router.register("privileges", PrivilegedViewSet)
router.register("server_privileges", ServerPrivilegedViewSet)

urlpatterns = [
    path(
        "server_config/<url>/",
        ServerConfigView.as_view(),
        name="server_config",
    ),
    path(
        "role_webhook/<url>/",
        RoleWebhookView.as_view(),
        name="role_webhook",
    ),
    path("", include(router.urls)),
]
