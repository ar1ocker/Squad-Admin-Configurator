from access.managers import AccessManager
from access.plugins import ApplyAblePlugin, CompoundPlugin, DjangoAccessPlugin

from .models import ServerPrivilegedPack

AccessManager.register_plugins(
    {
        ServerPrivilegedPack: CompoundPlugin(
            DjangoAccessPlugin(),
            ApplyAblePlugin(
                visible=lambda queryset, request: queryset.filter(managers=request.user),
                changeable=lambda queryset, request: queryset.filter(managers=request.user),
            ),
        )
    }
)
