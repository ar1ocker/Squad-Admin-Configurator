from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RotationDistribution


class GetCurrentRotationConfig(APIView):
    """Получение текущего списка карт"""

    permission_classes = []

    @extend_schema(
        methods=["get"],
        responses={
            (200, "text/plain;charset=UTF-8"): OpenApiResponse(OpenApiTypes.STR, description="Текст ротации"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не найдена"),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не активна"),
        },
    )
    def get(self, request, url: str) -> HttpResponse | Response:
        distrib = get_object_or_404(RotationDistribution.objects.select_related("rotation"), url=url)

        if distrib.is_active:
            return HttpResponse(
                distrib.format_config(distrib.get_current_pack()),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)


class GetNextRotationConfig(APIView):
    """Получение следующего в очереди списка карт"""

    permission_classes = []

    @extend_schema(
        methods=["get"],
        responses={
            (200, "text/plain;charset=UTF-8"): OpenApiResponse(OpenApiTypes.STR, "Текст ротации"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, "Ротация не найдена"),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, "Ротация не активна"),
        },
    )
    def get(self, request, url: str) -> HttpResponse | Response:
        distrib = get_object_or_404(RotationDistribution.objects.select_related("rotation"), url=url)

        if distrib.is_active:
            return HttpResponse(
                distrib.format_config(distrib.get_next_pack()),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)
