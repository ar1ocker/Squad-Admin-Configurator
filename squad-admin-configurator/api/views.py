from datetime import timedelta

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from server_admins.models import Permission, Privileged, Role, Server, ServerPrivileged
from server_admins.services.server_config import server__generate_config

from .models import AdminsConfigDistribution, RoleWebhook, WebhookLog
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
        webhook: RoleWebhook = get_object_or_404(RoleWebhook, url=url)

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

        date_of_end = self._calc_date_of_end(webhook, serializer)

        with transaction.atomic():
            priv_defaults = {
                "name": serializer.validated_data["name"],
                "description": serializer.validated_data["comment"],
            }

            if webhook.set_common_date_of_end:
                priv_defaults["date_of_end"] = date_of_end

            priv, created = Privileged.objects.get_or_create(
                steam_id=serializer.validated_data["steam_id"],
                defaults=priv_defaults,
            )

            if not created and webhook.active_and_increase_common_date_of_end:
                need_save = False
                if not priv.is_active:
                    priv.is_active = True
                    need_save = True

                if priv.date_of_end is not None and priv.date_of_end < date_of_end:
                    priv.date_of_end = date_of_end
                    need_save = True

                if need_save:
                    priv.save()

            roles_ids = webhook.roles.values_list("pk", flat=True)

            for server_id in webhook.servers.values_list("pk", flat=True):
                server_priv = ServerPrivileged.objects.create(
                    server_id=server_id,
                    privileged=priv,
                    date_of_end=date_of_end,
                    comment=serializer.validated_data["comment"],
                )

                server_priv.roles.add(*roles_ids)

            webhook.write_log(
                f"Добавлены роли {serializer.validated_data}",
                log_level=WebhookLog.INFO,
                request=request,
            )

        return Response(data={"detail": "Created"})

    def _calc_date_of_end(self, webhook: RoleWebhook, serializer: RoleWebhookSerializer):
        duration: int

        if webhook.allow_custom_duration_until_end and serializer.validated_data["duration_until_end"]:
            duration = serializer.validated_data["duration_until_end"]
        elif webhook.duration_until_end is not None:
            duration = webhook.duration_until_end
        else:
            return None

        return timezone.now() + timedelta(**{webhook.unit_of_duration: duration})


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


class ServerViewSet(ModelViewSet):
    """View set для доступа к списку серверов"""

    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active", "title", "id"]


class PermissionViewSet(ModelViewSet):
    """View set для доступа к списку разрешений"""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title"]


class RoleViewSet(ModelViewSet):
    """View set для доступа к списку ролей"""

    queryset = Role.objects.prefetch_related("permissions").all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "is_active", "permissions"]

    def get_queryset(self):
        base_manager = Role.objects.prefetch_related("permissions")

        server_privileges_pk: str | None = self.kwargs.get("server_privileges_pk")
        if server_privileges_pk:
            return base_manager.filter(serverprivileged=server_privileges_pk).all()

        return base_manager.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RoleSerializer
        else:
            return RoleSerializerWrite


class PrivilegedViewSet(ModelViewSet):
    """View set для доступа к привилегированным пользователям"""

    queryset = Privileged.objects.prefetch_related("serverprivileged_set__roles", "serverprivileged_set__server").all()
    serializer_class = PrivilegedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "steam_id", "is_active"]


class ServerPrivilegedViewSet(ModelViewSet):
    """View set для доступа к привилегированным пользователям на серверах"""

    queryset = ServerPrivileged.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["server", "privileged", "roles", "is_active"]

    def get_queryset(self):
        base_manager = ServerPrivileged.objects.prefetch_related("roles").select_related("server")

        privileged_pk: str | None = self.kwargs.get("privileged_pk")
        if privileged_pk:
            return base_manager.filter(privileged=privileged_pk).all()

        return base_manager.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ServerPrivilegedSerializer
        else:
            return ServerPrivilegedSerializerWrite


class WebhookLogViewSet(ReadOnlyModelViewSet):
    """View set только на чтение для доступа к логам вебхуков"""

    queryset = WebhookLog.objects.all()
    serializer_class = WebhookLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["level"]
