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
)

app_name = "api"

router = SimpleRouter()

router.register("servers", ServerViewSet)
router.register("permissions", PermissionViewSet)
router.register("roles", RoleViewSet)
router.register("privileges", PrivilegedViewSet)
router.register("servers_privileges", ServerPrivilegedViewSet)

nested_privileges = NestedSimpleRouter(router, "privileges", lookup="privileged")
nested_privileges.register("servers_roles", ServerPrivilegedViewSet)

nested_servers_roles_router = NestedSimpleRouter(nested_privileges, "servers_roles", lookup="server_privileges")
nested_servers_roles_router.register("roles", RoleViewSet)

nested_server_privileges_router = NestedSimpleRouter(router, "servers_privileges", lookup="server_privileges")
nested_server_privileges_router.register("roles", RoleViewSet)

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
    path("", include(nested_privileges.urls)),
    path("", include(nested_servers_roles_router.urls)),
    path("", include(nested_server_privileges_router.urls)),
]
