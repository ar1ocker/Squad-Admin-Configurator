from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers
from server_admins.models import Permission, Privileged, Role, Server, ServerPrivileged

from .models import WebhookLog


class RoleWebhookSerializer(serializers.Serializer):
    steam_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    duration_until_end = serializers.IntegerField(required=False, default=None)
    comment = serializers.CharField(max_length=200)


class ServerSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"


class PermissionSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class RoleSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = "__all__"


class RoleSerializerWrite(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Role
        fields = "__all__"


class ServerPrivilegedSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    server = ServerSerializer(read_only=True)

    class Meta:
        model = ServerPrivileged
        fields = "__all__"


class ServerPrivilegedSerializerWrite(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, allow_null=True)
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.all())

    class Meta:
        model = ServerPrivileged
        fields = "__all__"


class PrivilegedSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    servers_roles = ServerPrivilegedSerializer(source="serverprivileged_set", many=True, read_only=True)

    class Meta:
        model = Privileged
        fields = "__all__"


class WebhookLogSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = "__all__"
