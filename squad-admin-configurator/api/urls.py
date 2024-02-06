from django.urls import path

from .views import RoleWebhookView, ServerConfigView

app_name = "api"

urlpatterns = [
    path(
        "server_config/<url>/",
        ServerConfigView.as_view(),
        name="server_config",
    ),
    path(
        "role_webhook/<url>/", RoleWebhookView.as_view(), name="role_webhook"
    ),
]
