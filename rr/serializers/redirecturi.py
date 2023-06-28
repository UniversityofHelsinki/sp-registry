import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.redirecturi import RedirectUri, redirecturi_validator
from rr.serializers.common import ActiveListSerializer

logger = logging.getLogger(__name__)


class RedirectUriSerializer(serializers.ModelSerializer):
    def validate(self, data):
        sp = data["sp"] if "sp" in data else self.instance.sp
        uri = data["uri"] if "uri" in data else None
        redirecturi_validator(sp, uri, serializers.ValidationError)
        return data

    class Meta:
        model = RedirectUri
        fields = ["id", "sp", "uri", "created_at", "updated_at", "end_at", "validated", "status"]
        read_only_fields = ["created_at", "updated_at", "end_at", "validated", "status"]

        validators = [UniqueTogetherValidator(queryset=RedirectUri.objects.filter(end_at=None), fields=["sp", "uri"])]

    def create(self, validated_data):
        redirecturi = RedirectUri.objects.create(**validated_data)
        user = self.context["request"].user
        logger.info("Redirect URI added for {sp} by {user}".format(sp=redirecturi.sp, user=user))
        return redirecturi


class RedirectUriLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = ActiveListSerializer
        model = RedirectUri
        fields = ["id", "uri", "status"]
        read_only_fields = ["status"]
