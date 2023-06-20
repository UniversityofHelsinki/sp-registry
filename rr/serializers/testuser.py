import hashlib
import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider
from rr.models.testuser import TestUser, TestUserData
from rr.serializers.common import ActiveListSerializer

logger = logging.getLogger(__name__)


class TestUserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for test user data
    """

    attribute = serializers.SlugRelatedField(
        read_only=False, slug_field="friendlyname", queryset=Attribute.objects.all()
    )

    class Meta:
        model = TestUserData
        fields = ("id", "user", "attribute", "value")


class TestUserDataLimitedSerializer(TestUserDataSerializer):
    class Meta:
        model = TestUserData
        fields = ("id", "attribute", "value")


class TestUserSerializer(serializers.ModelSerializer):
    """
    Serializer for test users
    """

    attributes = TestUserDataLimitedSerializer(many=True, required=False)
    valid_for = serializers.SlugRelatedField(
        many=True,
        required=False,
        slug_field="entity_id",
        read_only=False,
        queryset=ServiceProvider.objects.filter(end_at=None),
    )

    class Meta:
        model = TestUser
        fields = ("id", "sp", "username", "password", "firstname", "lastname", "valid_for", "attributes")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = self.context["request"].user
        attributes = validated_data.pop("attributes", None)
        valid_for = validated_data.pop("valid_for", None)
        validated_data["password"] = hashlib.sha256(validated_data["password"].encode("utf-8")).hexdigest()
        testuser = TestUser.objects.create(**validated_data)
        testuser.valid_for.add(testuser.sp)
        logger.info(
            "Test user {username} added for {sp} by {user}".format(
                username=testuser.username, sp=testuser.sp, user=user
            )
        )
        if valid_for:
            for sp in valid_for:
                testuser.valid_for.add(sp)
        if attributes:
            for attribute in attributes:
                if "value" in attribute and attribute["value"]:
                    TestUserData.objects.create(
                        user=testuser, attribute=attribute["attribute"], value=attribute["value"]
                    )
        return testuser

    def update(self, instance, validated_data):
        user = self.context["request"].user
        attributes = validated_data.pop("attributes", None)
        valid_for = validated_data.pop("valid_for", None)
        for field in validated_data:
            if field == "password":
                setattr(instance, field, hashlib.sha256(validated_data[field].encode("utf-8")).hexdigest())
            else:
                setattr(instance, field, validated_data[field])
        instance.save()
        logger.info(
            "Test user {username} modified for {sp} by {user}".format(
                username=instance.username, sp=instance.sp, user=user
            )
        )
        if valid_for:
            for sp in instance.valid_for.all():
                if sp not in valid_for and sp is not instance:
                    instance.valid_for.remove(sp)
            for sp in valid_for:
                instance.valid_for.add(sp)
        if attributes:
            for attribute in attributes:
                if "value" in attribute and attribute["value"]:
                    try:
                        obj = TestUserData.objects.get(user=instance, attribute=attribute["attribute"])
                        if obj.value != attribute["value"]:
                            obj.value = attribute["value"]
                            obj.save()
                    except TestUserData.DoesNotExist:
                        TestUserData.objects.get_or_create(
                            user=instance, attribute=attribute["attribute"], value=attribute["value"]
                        )
                elif "attribute" in attribute:
                    TestUserData.objects.filter(user=instance, attribute=attribute["attribute"]).delete()
        return instance

    def validate_sp(self, value):
        user = self.context["request"].user
        if not user.is_superuser and user not in value.admins.all():
            raise serializers.ValidationError(_("No permissions for SP"))
        return value

    def validate_valid_for(self, value):
        user = self.context["request"].user
        if value and not user.is_superuser:
            for sp in value:
                if user not in sp.admins.all():
                    raise serializers.ValidationError(_("No permissions for SP"))
        return value


class TestUserLimitedSerializer(TestUserSerializer):
    class Meta:
        list_serializer_class = ActiveListSerializer
        model = TestUser
        fields = ("id", "username", "password", "firstname", "lastname", "valid_for", "attributes")
        extra_kwargs = {"password": {"write_only": True}}
