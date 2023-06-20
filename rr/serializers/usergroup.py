import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.usergroup import UserGroup
from rr.serializers.common import ActiveListSerializer

logger = logging.getLogger(__name__)


class UserGroupSerializer(serializers.ModelSerializer):
    def validate(self, data):
        sp = data["sp"] if "sp" in data else self.instance.sp
        name = data["name"] if "name" in data else None
        if UserGroup.objects.filter(sp=sp, name=name, end_at=None).exists():
            raise serializers.ValidationError(_("Group already added"))
        return data

    class Meta:
        model = UserGroup
        fields = ["id", "sp", "name", "created_at", "updated_at", "end_at", "validated", "status"]
        read_only_fields = ["created_at", "updated_at", "end_at", "validated", "status"]

        validators = [UniqueTogetherValidator(queryset=UserGroup.objects.filter(end_at=None), fields=["sp", "name"])]

    def create(self, validated_data):
        usergroup = UserGroup.objects.create(**validated_data)
        user = self.context["request"].user
        logger.info("UserGroup added for {sp} by {user}".format(sp=usergroup.sp, user=user))
        return usergroup


class UserGroupLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = ActiveListSerializer
        model = UserGroup
        fields = ["id", "name", "status"]
        read_only_fields = ["status"]
