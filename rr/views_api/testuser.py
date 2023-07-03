import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from rr.models.testuser import TestUser, TestUserData
from rr.serializers.testuser import TestUserDataSerializer, TestUserSerializer

logger = logging.getLogger(__name__)


class TestUserViewSet(viewsets.ModelViewSet):
    """API endpoint for test users
    list:
    Returns a list of all the existing test users.
    retrieve:
    Returns the given test user.
    create:
    Creates a new test user instance.
    update:
    Updates a given test user.
    partial_update:
    Updates a given test user.
    destroy:
    Removes the given test user.
    """

    queryset = TestUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TestUserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["username", "sp__entity_id", "valid_for__entity_id"]
    filterset_fields = [
        "username",
        "sp",
        "attributes__attribute__friendlyname",
        "attributes__value",
        "sp__entity_id",
        "valid_for__entity_id",
    ]

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info(
            "Test user {username} removed from {sp} by {user}".format(
                username=instance.username, sp=instance.sp, user=self.request.user
            )
        )

    def get_queryset(self):
        """
        Restricts the returned information to test users in services user has admin access
        """
        user = self.request.user

        if not user.is_superuser:
            self.queryset = self.queryset.filter(sp__admins=user, end_at=None)
        return self.queryset


class TestUserDataViewSet(viewsets.ModelViewSet):
    """API endpoint for test user attributes
    list:
    Returns a list of all the existing test user attributes.
    retrieve:
    Returns the given test user attribute.
    create:
    Creates a new test user attribute instance.
    update:
    Updates a given test user attribute.
    partial_update:
    Updates a given test user attribute.
    destroy:
    Removes the given test user attribute.
    """

    queryset = TestUserData.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TestUserDataSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["attribute__friendlyname", "user__username", "value"]
    filterset_fields = ["attribute__friendlyname", "user__username"]

    def get_queryset(self):
        """
        Restricts the returned information to test users in services user has admin access
        """
        user = self.request.user
        if not user.is_superuser:
            self.queryset = self.queryset.filter(user__sp__admins=user)
        return self.queryset
