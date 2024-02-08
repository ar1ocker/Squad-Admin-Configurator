from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RotationDistribution


class GetCurrentRotationConfig(APIView):
    """Получение текущего списка карт"""

    permission_classes = []

    def get(self, request, url):
        distrib = get_object_or_404(
            RotationDistribution.objects.select_related("rotation"), url=url
        )

        if distrib.is_active:
            return HttpResponse(
                distrib.format_config(distrib.get_current_pack()),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)


class GetNextRotationConfig(APIView):
    """Получение следующего в очереди списка карт"""

    permission_classes = []

    def get(self, request, url):
        distrib = get_object_or_404(
            RotationDistribution.objects.select_related("rotation"), url=url
        )

        if distrib.is_active:
            return HttpResponse(
                distrib.format_config(distrib.get_next_pack()),
                content_type="text/plain;charset=UTF-8",
            )

        return Response(status=status.HTTP_403_FORBIDDEN)
