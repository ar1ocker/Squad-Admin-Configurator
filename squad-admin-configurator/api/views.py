from datetime import timedelta

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from server_admins.models import Privileged, ServerPrivileged

from .models import RoleWebhook, ServerUrl, WebhookLog
from .request_validators import validate_hmac_in_request
from .serializers import RoleWebhookSerializer


class RoleWebhookView(APIView):
    """
    Добавление новых ролей пользователям при вызове вебхука
    """

    def post(self, request: Request, url):
        webhook = get_object_or_404(
            RoleWebhook,
            url=url
        )

        if not webhook.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            validate_hmac_in_request(request, webhook)
        except ValidationError as error:
            webhook.write_log(
                f'Ошибка валидации HMAC - {error.detail}',
                log_level=WebhookLog.WARNING,
                request=request
            )
            raise error

        serializer = RoleWebhookSerializer(data=request.data)

        if not serializer.is_valid():
            webhook.write_log(
                f'Ошибка проверки запроса сериализатором {serializer.errors}',
                log_level=WebhookLog.WARNING,
                request=request
            )
            raise ValidationError(serializer.errors)

        if webhook.allow_custom_duration_until_end:
            duration = (serializer.validated_data['duration_until_end']
                        or webhook.duration_until_end)
            date_of_end = (timezone.now()
                           + timedelta(**{webhook.unit_of_duration: duration}))
        else:
            date_of_end = (
                timezone.now()
                + timedelta(**{webhook.unit_of_duration:
                               webhook.duration_until_end})
            )

        with transaction.atomic():
            priv, created = (
                Privileged.objects
                .get_or_create(
                    steam_id=serializer.validated_data['steam_id'],
                    defaults=(
                        {'name': serializer.validated_data['name'],
                         'description': serializer.validated_data['comment'],
                         'date_of_end': date_of_end}
                    )
                )
            )

            if not created and webhook.active_and_increase_common_date_of_end:
                need_save = False
                if not priv.is_active:
                    priv.is_active = True
                    need_save = True

                if (priv.date_of_end is not None
                        and priv.date_of_end < date_of_end):
                    priv.date_of_end = date_of_end
                    need_save = True

                if need_save:
                    priv.save()

            roles_ids = webhook.roles.values_list('pk', flat=True)

            for server_id in webhook.servers.values_list('pk', flat=True):
                server_priv = ServerPrivileged.objects.create(
                    server_id=server_id,
                    privileged=priv,
                    date_of_end=date_of_end,
                    comment=serializer.validated_data['comment']
                )

                server_priv.roles.add(*roles_ids)

            webhook.write_log(
                f'Добавлены роли {serializer.validated_data}',
                log_level=WebhookLog.INFO,
                request=request
            )

        return Response(data={'detail': 'Created'})


class ServerConfigView(APIView):
    """
    Получение конфигурации администраторов игрового сервера по get запросу
    с определенным постфиксом
    """

    def get(self, request, url):
        server_url = get_object_or_404(
            ServerUrl.objects.select_related('server'),
            url=url
        )
        if server_url.is_active:
            return HttpResponse(server_url.server.get_config(),
                                content_type='text/plain;charset=UTF-8')

        return Response(status=status.HTTP_403_FORBIDDEN)
