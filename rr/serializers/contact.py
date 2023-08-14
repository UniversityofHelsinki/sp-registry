import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.contact import Contact

logger = logging.getLogger(__name__)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "sp",
            "type",
            "firstname",
            "lastname",
            "email",
            "created_at",
            "updated_at",
            "end_at",
            "validated",
            "status",
        ]
        read_only_fields = ["created_at", "updated_at", "end_at", "validated", "status"]

        validators = [
            UniqueTogetherValidator(
                queryset=Contact.objects.filter(end_at=None), fields=["sp", "type", "firstname", "lastname", "email"]
            )
        ]

    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        user = self.context["request"].user
        logger.info("Contact added for {sp} by {user}".format(sp=contact.sp, user=user))
        return contact


class ContactLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "type", "firstname", "lastname", "email", "status"]
        read_only_fields = ["status"]
