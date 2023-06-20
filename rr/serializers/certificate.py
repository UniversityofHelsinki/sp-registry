import logging

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rr.models.certificate import Certificate, certificate_validator
from rr.serializers.common import ActiveListSerializer

logger = logging.getLogger(__name__)


class CertificateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        sp = data["sp"] if "sp" in data else self.instance.sp
        certificate = data["certificate"] if "certificate" in data else None
        signing = data["signing"] if "signing" in data else False
        encryption = data["encryption"] if "encryption" in data else False
        if not signing and not encryption:
            signing = True
            encryption = True
        certificate_validator(sp, certificate, signing, encryption, serializers.ValidationError)
        return data

    class Meta:
        model = Certificate
        fields = [
            "id",
            "sp",
            "cn",
            "issuer",
            "valid_from",
            "valid_until",
            "key_size",
            "certificate",
            "signing",
            "encryption",
            "created_at",
            "updated_at",
            "end_at",
            "validated",
            "status",
        ]
        read_only_fields = [
            "cn",
            "issuer",
            "valid_from",
            "valid_until",
            "key_size",
            "created_at",
            "updated_at",
            "end_at",
            "validated",
            "status",
        ]

        validators = [
            UniqueTogetherValidator(
                queryset=Certificate.objects.filter(end_at=None), fields=["sp", "certificate", "signing", "encryption"]
            )
        ]

    def create(self, validated_data):
        sp = validated_data.pop("sp", None)
        certificate = (
            validated_data.pop("certificate", None)
            .replace("-----BEGIN CERTIFICATE-----", "")
            .replace("-----END CERTIFICATE-----", "")
            .strip()
        )
        encryption = validated_data.pop("encryption", False)
        signing = validated_data.pop("signing", False)
        if not signing and not encryption:
            signing = True
            encryption = True
        cert = Certificate.objects.add_certificate(certificate, sp, signing=signing, encryption=encryption)
        user = self.context["request"].user
        logger.info("Certificate added for {sp} by {user}".format(sp=sp, user=user))
        return cert


class CertificateLimitedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = ActiveListSerializer
        model = Certificate
        fields = ["id", "sp", "valid_from", "valid_until", "certificate", "signing", "encryption", "status"]
        read_only_fields = ["valid_from", "valid_until", "status"]
