from django.urls import include, path
from rest_framework_nested.routers import NestedSimpleRouter, SimpleRouter

from .views import (
    PermissionViewSet,
    PrivilegedViewSet,
    RoleViewSet,
    RoleWebhookView,
    ServerConfigView,
    ServerPrivilegedViewSet,
    ServerViewSet,
    WebhookLogViewSet,
)

app_name = "api"

router = SimpleRouter()

router.register("servers", ServerViewSet)
router.register("permissions", PermissionViewSet)
router.register("roles", RoleViewSet)
router.register("privileges", PrivilegedViewSet)
router.register("servers_privileges", ServerPrivilegedViewSet)
router.register("webhook", WebhookLogViewSet)

urlpatterns = [
    path(
        "server_config/<str:url>/",
        ServerConfigView.as_view(),
        name="server_config",
    ),
    path(
        "role_webhook/<str:url>/",
        RoleWebhookView.as_view(),
        name="role_webhook",
    ),
    path("", include(router.urls)),
]
