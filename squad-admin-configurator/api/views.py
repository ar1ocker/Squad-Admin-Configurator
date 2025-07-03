from api.services.role_webhook import role_webhook__create_server_privileges
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from server_admins.models import Permission, Privileged, Role, Server, ServerPrivileged
from server_admins.services.server_config import server__generate_config

from .filters import PrivilegedFilter, RoleFilter, ServerFilter, ServerPrivilegedFilter
from .models import AdminsConfigDistribution, RoleWebhook, WebhookLog
from .pagination import DefaultLimitOffsetPagination
from .serializers import (
    PermissionSerializer,
    PrivilegedSerializer,
    RoleSerializer,
    RoleSerializerWrite,
    RoleWebhookSerializer,
    ServerPrivilegedSerializer,
    ServerPrivilegedSerializerWrite,
    ServerSerializer,
    WebhookLogSerializer,
)


class RoleWebhookView(GenericAPIView):
    """
    Добавление новых ролей пользователям при вызове вебхука post запросом
    """

    serializer_class = RoleWebhookSerializer
    permission_classes = []

    @extend_schema(
        responses={
            200: OpenApiResponse(
                OpenApiTypes.JSON_PTR,
                "Создано",
                examples=[OpenApiExample("Пример", {"detail": "created"})],
            ),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, "Вебхук не активен"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, "Вебхук не найден"),
        }
    )
    def post(self, request: Request, url: str) -> Response:
        webhook: RoleWebhook = get_object_or_404(RoleWebhook.objects.prefetch_related("servers", "roles"), url=url)

        if not webhook.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            webhook.validate_request(request)
        except ValidationError as error:
            webhook.write_log(
                f"Ошибка валидации HMAC - {error.detail}",
                log_level=WebhookLog.WARNING,
                request=request,
            )
            raise error

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            webhook.write_log(
                f"Ошибка проверки запроса сериализатором {serializer.errors}",
                log_level=WebhookLog.WARNING,
                request=request,
            )
            raise ValidationError(serializer.errors)

        steam_id = serializer.validated_data["steam_id"]
        name = serializer.validated_data["name"]
        comment = serializer.validated_data["comment"]
        duration_until_end = serializer.validated_data["duration_until_end"]

        role_webhook__create_server_privileges(
            webhook=webhook, steam_id=steam_id, name=name, duration_until_end=duration_until_end, comment=comment
        )

        webhook.write_log(
            f"Добавлены роли {serializer.validated_data}",
            log_level=WebhookLog.INFO,
            request=request,
        )

        return Response(data={"detail": "Created"})


class ServerConfigView(APIView):
    """
    Получение конфигурации администраторов игрового сервера по get запросу
    с определенным постфиксом
    """

    permission_classes = []

    @extend_schema(
        methods=["get"],
        responses={
            (200, "text/plain;charset=UTF-8"): OpenApiResponse(OpenApiTypes.STR, "Текст конфига сервера"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, "Сервер не найден"),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, "Сервер не активен"),
        },
    )
    def get(self, request: Request, url: str) -> HttpResponse | Response:
        server_url = get_object_or_404(
            AdminsConfigDistribution.objects.select_related("server"),
            url=url,
        )

        if server_url.is_active:
            return HttpResponse(
                server__generate_config(server=server_url.server),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)


class ServerViewSet(viewsets.ModelViewSet):
    """View set для доступа к списку серверов"""

    queryset = Server.objects.all()
    pagination_class = DefaultLimitOffsetPagination
    serializer_class = ServerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServerFilter


class PermissionViewSet(viewsets.ModelViewSet):
    """View set для доступа к списку разрешений"""

    queryset = Permission.objects.all()
    pagination_class = DefaultLimitOffsetPagination
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "title": ["exact", "icontains"],
        "description": ["exact", "icontains"],
    }


class RoleViewSet(viewsets.ModelViewSet):
    """View set для доступа к списку ролей"""

    queryset = Role.objects.all()
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoleFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RoleSerializer
        else:
            return RoleSerializerWrite


class PrivilegedViewSet(viewsets.ModelViewSet):
    """View set для доступа к привилегированным пользователям"""

    queryset = Privileged.objects.all()
    pagination_class = DefaultLimitOffsetPagination
    serializer_class = PrivilegedSerializer
    filter_backends: list[type[DjangoFilterBackend]] = [DjangoFilterBackend]
    filterset_class = PrivilegedFilter


class ServerPrivilegedViewSet(viewsets.ModelViewSet):
    """View set для доступа к привилегированным пользователям на серверах"""

    queryset = ServerPrivileged.objects.select_related("privileged", "server").prefetch_related("roles").all()
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServerPrivilegedFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ServerPrivilegedSerializer
        else:
            return ServerPrivilegedSerializerWrite


class WebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View set только на чтение для доступа к логам вебхуков"""

    queryset = WebhookLog.objects.all()
    serializer_class = WebhookLogSerializer
    pagination_class = DefaultLimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["level"]
