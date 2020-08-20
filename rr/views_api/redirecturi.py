import logging

from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rr.models.redirecturi import RedirectUri
from rr.serializers.redirecturi import RedirectUriSerializer
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class RedirectUriViewSet(CustomModelViewSet):
    """API endpoint for redirect URIs
    list:
    Returns a list of all the existing redirect URIs.
    retrieve:
    Returns the given redirect URI.
    create:
    Creates a new endpoint redirect URI.
    destroy:
    Removes the given redirect URI.
    """
    queryset = RedirectUri.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RedirectUriSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['uri']
    filterset_fields = ['sp', 'uri']

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("Redirect URI removed from {service} by {user}"
                    .format(service=instance.sp, user=self.request.user))
