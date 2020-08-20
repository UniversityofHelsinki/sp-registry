from rest_framework import routers

from rr.views_api.contact import ContactViewSet
from rr.views_api.endpoint import EndpointViewSet
from rr.views_api.redirecturi import RedirectUriViewSet
from rr.views_api.serviceprovider import SamlServiceProviderViewSet, SPAttributeViewSet
from rr.views_api.serviceprovider import OidcServiceProviderViewSet, LdapServiceProviderViewSet
from rr.views_api.testuser import TestUserViewSet, TestUserDataViewSet
from rr.views_api.usergroup import UserGroupViewSet

router = routers.DefaultRouter()
router.register(r'attributes', SPAttributeViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'endpoints', EndpointViewSet)
router.register(r'redirecturis', RedirectUriViewSet)
router.register(r'services/saml', SamlServiceProviderViewSet)
router.register(r'services/oidc', OidcServiceProviderViewSet)
router.register(r'services/ldap', LdapServiceProviderViewSet)
router.register(r'testusers', TestUserViewSet)
router.register(r'testuserdata', TestUserDataViewSet)
router.register(r'usergroups', UserGroupViewSet)