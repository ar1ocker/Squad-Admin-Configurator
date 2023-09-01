from rest_framework import serializers


class RoleWebhookSerializer(serializers.Serializer):
    steam_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    duration_until_end = serializers.IntegerField(
        required=False,
        default=None
    )
    comment = serializers.CharField(max_length=200)
