from rest_framework import routers

from rr.views_api.certificate import CertificateViewSet
from rr.views_api.contact import ContactViewSet
from rr.views_api.endpoint import EndpointViewSet
from rr.views_api.redirecturi import RedirectUriViewSet
from rr.views_api.serviceprovider import (
    LdapServiceProviderViewSet,
    OidcServiceProviderViewSet,
    SamlServiceProviderViewSet,
    SPAttributeViewSet,
)
from rr.views_api.testuser import TestUserDataViewSet, TestUserViewSet
from rr.views_api.usergroup import UserGroupViewSet

router = routers.DefaultRouter()
router.register(r"attributes", SPAttributeViewSet)
router.register(r"certificates", CertificateViewSet)
router.register(r"contacts", ContactViewSet)
router.register(r"endpoints", EndpointViewSet)
router.register(r"redirecturis", RedirectUriViewSet)
router.register(r"services/saml", SamlServiceProviderViewSet, basename="service-saml")
router.register(r"services/oidc", OidcServiceProviderViewSet, basename="service-oidc")
router.register(r"services/ldap", LdapServiceProviderViewSet, basename="service-ldap")
router.register(r"testusers", TestUserViewSet)
router.register(r"testuserdata", TestUserDataViewSet)
router.register(r"usergroups", UserGroupViewSet)
