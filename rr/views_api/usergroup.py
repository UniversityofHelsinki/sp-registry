import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rr.models.usergroup import UserGroup
from rr.serializers.usergroup import UserGroupSerializer
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class UserGroupViewSet(CustomModelViewSet):
    """API endpoint for user groups
    list:
    Returns a list of all the existing user groups.
    retrieve:
    Returns the given user group.
    create:
    Creates a new endpoint user group.
    destroy:
    Removes the given user group.
    """

    queryset = UserGroup.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserGroupSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["sp", "name"]

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("User group removed from {service} by {user}".format(service=instance.sp, user=self.request.user))
