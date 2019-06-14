import json
import os

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.attribute import Attribute
from rr.models.oidc import GrantType, OIDCScope, ResponseType
from rr.models.redirecturi import RedirectUri
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.utils.oidc_metadata_generator import oidc_metadata_generator

TESTDATA_OIDC_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/metadata_oidc.json')


class ServiceProviderOIDCTechnicalTestCase(TestCase):
    fixtures = ['rr/fixtures/oidc.json']
    test_metadata = ''
    maxDiff = None

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='oidc')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp',
                                                      service_type='oidc',
                                                      name_en="SP2 Example service",
                                                      privacypolicy_fi="https://example.org/privacyfi")
        self.user_sp.admins.add(self.user)

    def test_sp_oidc_view_denies_anonymous(self):
        response = self.client.get(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}))

    def test_sp_oidc_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('oidc-technical-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_sp_oidc_view_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sp_oidc_entity_id_change(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'entity_id': 'test:entity:1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Client ID already exists', response.content.decode())
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'entity_id': 'https://sp2.example.org/sp/valid'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Client ID already exists', response.content.decode())
        self.assertIn('https://sp2.example.org/sp/valid', response.content.decode())

    def test_sp_oidc_grant_and_response_type(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'response_types': '1', 'grant_types': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('authorization_code Grant type must be set for code Response type.', response.content.decode())
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'response_types': ['1', '2', '3'], 'grant_types': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('authorization_code Grant type must be set for code Response type.', response.content.decode())
        response = self.client.post(reverse('oidc-technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'response_types': ['1', '2', '3'], 'grant_types': ['1', '2']})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('authorization_code Grant type must be set for code Response type.', response.content.decode())

    def test_sp_oidc_metadata(self):
        self.client.force_login(self.user)
        RedirectUri.objects.create(sp=self.user_sp, uri='https://sp2.example.org/redirect_uri')
        self.user_sp.grant_types.add(GrantType.objects.filter(name="authorization_code").first())
        self.user_sp.response_types.add(ResponseType.objects.filter(name="code").first())
        self.user_sp.response_types.add(ResponseType.objects.filter(name="id_token").first())
        self.user_sp.oidc_scopes.add(OIDCScope.objects.filter(name="profile").first())
        self.attr_eppn = Attribute.objects.create(friendlyname='eduPersonPrincipalName',
                                                  name='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                                                  attributeid='id-urn:mace:dir:attribute-def:eduPersonPrincipalName',
                                                  nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                  public_saml=True,
                                                  public_ldap=False,
                                                  public_oidc=True,
                                                  oidc_claim="eppn")
        SPAttribute.objects.create(attribute=self.attr_eppn, sp=self.user_sp, reason='User identification',
                                   oidc_userinfo=True)
        self.user_sp.encrypted_client_secret = "abc"
        self.user_sp.application_type = "web"
        self.user_sp.save()
        metadata = oidc_metadata_generator(sp=self.user_sp, validated=False)
        self.assertEqual(json.dumps(metadata, indent=4, sort_keys=True) + '\n', open(TESTDATA_OIDC_FILENAME).read())
