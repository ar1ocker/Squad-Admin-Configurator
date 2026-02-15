from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import RotationDistribution


class RotationDistributionViewSet(ViewSet):
    permission_classes = []
    authentication_classes = []

    @action(methods=["get"], detail=False, url_path="<str:url>", url_name="current")
    @extend_schema(
        methods=["get"],
        responses={
            (200, "text/plain;charset=UTF-8"): OpenApiResponse(OpenApiTypes.STR, description="Текст ротации"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не найдена"),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не активна"),
        },
    )
    def current(self, request, url: str) -> HttpResponse | Response:
        distrib = get_object_or_404(RotationDistribution.objects.select_related("rotation"), url=url)

        if distrib.is_active:
            return HttpResponse(
                distrib.format_config(distrib.get_current_pack()),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(methods=["get"], detail=False, url_path="<str:url>/<str:slug>", url_name="by_slug")
    @extend_schema(
        methods=["get"],
        responses={
            (200, "text/plain;charset=UTF-8"): OpenApiResponse(OpenApiTypes.STR, description="Текст ротации"),
            404: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не найдена"),
            403: OpenApiResponse(OpenApiTypes.JSON_PTR, description="Ротация не активна"),
        },
    )
    def by_slug(self, request, url: str, slug: str) -> HttpResponse | Response:
        distrib = get_object_or_404(RotationDistribution.objects.select_related("rotation"), url=url)

        if not distrib.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        pack = distrib.rotation.packs_through.filter(slug=slug).first()

        if pack is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(
            distrib.format_config(pack),
            content_type="text/plain;charset=UTF-8",
        )
