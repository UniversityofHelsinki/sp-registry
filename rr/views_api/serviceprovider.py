import logging

from django.utils import timezone

from django_filters import rest_framework as df_filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.widgets import BooleanWidget

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.serializers.serviceprovider import SamlServiceProviderSerializer, SPAttributeSerializer
from rr.serializers.serviceprovider import OidcServiceProviderSerializer, LdapServiceProviderSerializer
from rr.utils.serviceprovider import get_service_provider_queryset
from rr.views_api.common import CustomModelViewSet

logger = logging.getLogger(__name__)


class SPAttributeViewSet(CustomModelViewSet):
    """API endpoint for service provider attributes.

    list:
    Returns a list of all the existing service provider attributes.
    retrieve:
    Returns the given service provider attribute.
    create:
    Creates a new service provider attribute instance.
    update:
    Updates the given service provider attribute.
    partial_update:
    Updates the given service provider attribute.
    destroy:
    Removes the given service provider attribute.
    """
    queryset = SPAttribute.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SPAttributeSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['reason', 'sp', 'attribute']
    filterset_fields = ['sp', 'attribute']

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("Attribute requisition for {attribute} removed from {sp} by {user}"
                    .format(attribute=instance.attribute, sp=instance.sp,
                            user=self.request.user))


class ServiceProviderFilter(df_filters.FilterSet):
    """
    Filters for ServiceProvider view.
    """
    admins__username = df_filters.CharFilter(lookup_expr='icontains')
    admin_groups__name = df_filters.CharFilter(lookup_expr='icontains')
    notes = df_filters.CharFilter(lookup_expr='icontains')
    production = df_filters.BooleanFilter(field_name='production', widget=BooleanWidget())
    test = df_filters.BooleanFilter(field_name='test', widget=BooleanWidget())

    class Meta:
        model = ServiceProvider
        fields = ['entity_id', 'production', 'test', 'admins__username', 'admin_groups__name', 'notes']


class SamlServiceProviderViewSet(viewsets.ModelViewSet):
    """API endpoint for SAML service providers.

    list:
    Returns a list of all the existing SAML service providers.
    retrieve:
    Returns the given SAML service provider.
    create:
    Creates a new SAML service provider instance.
    update:
    Updates the given SAML service provider.
    partial_update:
    Updates the given SAML service provider.
    destroy:
    Removes the given SAML service provider.
    """
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SamlServiceProviderSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['entity_id']
    filterset_class = ServiceProviderFilter

    def get_queryset(self):
        """
        Restricts the returned information to services
        """
        return get_service_provider_queryset(user=self.request.user, service_type='saml')

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("ServiceProvider {service} deleted by {user}"
                    .format(service=instance, user=self.request.user))


class OidcServiceProviderViewSet(viewsets.ModelViewSet):
    """API endpoint for OIDC relying partys.

    list:
    Returns a list of all the existing OIDC relying partys.
    retrieve:
    Returns the given OIDC relying party.
    create:
    Creates a new OIDC relying party instance.
    update:
    Updates the given OIDC relying party.
    partial_update:
    Updates the given OIDC relying party.
    destroy:
    Removes the given OIDC relying party.
    """
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OidcServiceProviderSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['entity_id']
    filterset_class = ServiceProviderFilter

    def get_queryset(self):
        """
        Restricts the returned information to services
        """
        return get_service_provider_queryset(user=self.request.user, service_type='oidc')

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("ServiceProvider {service} deleted by {user}"
                    .format(service=instance, user=self.request.user))


class LdapServiceProviderViewSet(viewsets.ModelViewSet):
    """API endpoint for LDAP services.

    list:
    Returns a list of all the existing LDAP services.
    retrieve:
    Returns the given LDAP service.
    create:
    Creates a new service LDAP service.
    update:
    Updates the given LDAP service.
    partial_update:
    Updates the given LDAP service.
    destroy:
    Removes the given LDAP service.
    """
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LdapServiceProviderSerializer
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend]
    search_fields = ['entity_id']
    filterset_class = ServiceProviderFilter

    def get_queryset(self):
        """
        Restricts the returned information to services
        """
        return get_service_provider_queryset(user=self.request.user, service_type='ldap')

    def perform_destroy(self, instance):
        instance.end_at = timezone.now()
        instance.save()
        logger.info("ServiceProvider {service} deleted by {user}"
                    .format(service=instance, user=self.request.user))
