import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rr.models.certificate import Certificate
from rr.serializers.certificate import CertificateSerializer
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class CertificateViewSet(CustomModelViewSet):
    """API endpoint for certificates
    list:
    Returns a list of all the existing certificates.
    retrieve:
    Returns the given certificate.
    create:
    Creates a new certificate instance.
    destroy:
    Removes the given certificate.
    """

    queryset = Certificate.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CertificateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["cn", "key_size"]
    filterset_fields = ["sp", "cn", "encryption", "signing", "key_size"]

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("Certificate removed from {service} by {user}".format(service=instance.sp, user=self.request.user))
