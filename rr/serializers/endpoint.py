import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.endpoint import Endpoint, endpoint_validator
from rr.serializers.common import ActiveListSerializer

logger = logging.getLogger(__name__)


class EndpointSerializer(serializers.ModelSerializer):
    def validate(self, data):
        sp = data["sp"] if "sp" in data else self.instance.sp
        binding = data["binding"] if "binding" in data else None
        index = data["index"] if "index" in data else None
        is_default = data["is_default"] if "is_default" in data else None
        location = data["location"] if "location" in data else None
        endpoint_type = data["type"] if "type" in data else None
        endpoint_validator(sp, binding, index, is_default, location, endpoint_type, serializers.ValidationError)
        return data

    class Meta:
        model = Endpoint
        fields = [
            "id",
            "sp",
            "type",
            "binding",
            "location",
            "response_location",
            "index",
            "is_default",
            "created_at",
            "updated_at",
            "end_at",
            "validated",
            "status",
        ]
        read_only_fields = ["created_at", "updated_at", "end_at", "validated", "status"]

        validators = [
            UniqueTogetherValidator(
                queryset=Endpoint.objects.filter(end_at=None), fields=["sp", "type", "binding", "location"]
            )
        ]

    def create(self, validated_data):
        endpoint = Endpoint.objects.create(**validated_data)
        user = self.context["request"].user
        logger.info("Endpoint added for {sp} by {user}".format(sp=endpoint.sp, user=user))
        return endpoint


class EndpointLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = ActiveListSerializer
        model = Endpoint
        fields = ["id", "type", "binding", "location", "response_location", "index", "is_default", "status"]
        read_only_fields = ["status"]
