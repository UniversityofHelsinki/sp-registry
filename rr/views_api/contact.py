import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rr.models.contact import Contact
from rr.serializers.contact import ContactSerializer
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class ContactViewSet(CustomModelViewSet):
    """API endpoint for contacts
    list:
    Returns a list of all the existing contacts.
    retrieve:
    Returns the given contact.
    create:
    Creates a new contact instance.
    destroy:
    Removes the given contact.
    """

    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["lastname", "firstname", "email"]
    filterset_fields = ["sp", "lastname", "firstname", "email"]

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("Contact removed from {service} by {user}".format(service=instance.sp, user=self.request.user))
