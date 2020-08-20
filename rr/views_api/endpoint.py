import logging

from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rr.models.endpoint import Endpoint
from rr.serializers.endpoint import EndpointSerializer
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class EndpointViewSet(CustomModelViewSet):
    """API endpoint for endpoints
    list:
    Returns a list of all the existing endpoints.
    retrieve:
    Returns the given endpoint.
    create:
    Creates a new endpoint instance.
    destroy:
    Removes the given endpoint.
    """
    queryset = Endpoint.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = EndpointSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['location', 'response_location']
    filterset_fields = ['sp', 'type', 'binding', 'location', 'response_location', 'index', 'is_default']

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("Endpoint removed from {service} by {user}"
                    .format(service=instance.sp, user=self.request.user))
