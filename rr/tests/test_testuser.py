import hashlib

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.testuser import TestUser, TestUserData


class TestUserTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.saml_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml', test=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:2', service_type='saml', test=True)
        self.oidc_sp = ServiceProvider.objects.create(entity_id='test:entity:oidc', service_type='oidc',
                                                      test=True)
        self.saml_sp.admins.add(self.user)
        self.oidc_sp.admins.add(self.user)
        self.attr_cn = Attribute.objects.create(friendlyname='cn',
                                                name='urn:oid:2.5.4.3',
                                                attributeid='id-urn:mace:dir:attribute-def:cn',
                                                nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                public_saml=True,
                                                public_oidc=True)
        self.attr_eppn = Attribute.objects.create(friendlyname='eduPersonPrincipalName',
                                                  name='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                                                  attributeid='id-urn:mace:dir:attribute-def:eduPersonPrincipalName',
                                                  nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                  public_saml=True,
                                                  public_oidc=True)
        SPAttribute.objects.create(attribute=self.attr_cn, sp=self.saml_sp, reason='User name')
        SPAttribute.objects.create(attribute=self.attr_eppn, sp=self.saml_sp, reason='User identification')
        SPAttribute.objects.create(attribute=self.attr_eppn, sp=self.oidc_sp, reason='User identification',
                                   oidc_userinfo=True)
        self.testuser = TestUser.objects.create(sp=self.saml_sp, username="jack", password="secret", firstname="Jack",
                                                lastname="Tester")
        self.testuser.valid_for.add(self.saml_sp)

    def test_testuser_view_denies_anonymous(self):
        response = self.client.get(reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}))
        response = self.client.post(reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}))

    def test_testuser_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('testuser-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('testuser-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_testuser_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_testuser_view_list_oidc(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('testuser-list', kwargs={'pk': self.oidc_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_testuser_view_create(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}),
                                    {'add_testuser': 'ok',
                                     'username': 'jjohn',
                                     'password': 'secretword',
                                     'firstname': 'John',
                                     'lastname': 'Johnson',
                                     'valid_for': ['1', '3'],
                                     'userdata': 'checked'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test user added: jjohn', response.content.decode())
        self.assertEqual(TestUser.objects.filter(sp=self.saml_sp).count(), 2)
        test_jjohn = TestUser.objects.get(username="jjohn")
        self.assertEqual(TestUserData.objects.filter(attribute=self.attr_cn, user=test_jjohn,
                                                     value="John Johnson").count(), 1)

    def test_testuser_view_create_dublicate(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('testuser-list', kwargs={'pk': self.saml_sp.pk}),
                                    {'add_testuser': 'ok',
                                     'username': 'jack',
                                     'password': 'secretword',
                                     'firstname': 'John',
                                     'lastname': 'Johnson',
                                     'valid_for': ['1'],
                                     'userdata': 'checked'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Username already exists', response.content.decode())
        self.assertEqual(TestUser.objects.filter(sp=self.saml_sp).count(), 1)

    def test_testuser_view_change_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('testuser-attribute-data', kwargs={'pk': self.testuser.pk}),
                                    {'update_user': 'ok',
                                     'password': '',
                                     'firstname': 'John',
                                     'lastname': 'Johnson',
                                     'valid_for': ['1', '3']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('User info updated: jack', response.content.decode())
        self.assertEqual(TestUser.objects.filter(sp=self.saml_sp).count(), 1)
        test_jack = TestUser.objects.get(username="jack")
        self.assertTrue(self.oidc_sp in test_jack.valid_for.all())
        self.assertEqual(test_jack.password, "secret")

    def test_testuser_view_change_password(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('testuser-attribute-data', kwargs={'pk': self.testuser.pk}),
                                    {'update_user': 'ok',
                                     'password': 'word',
                                     'firstname': 'John',
                                     'lastname': 'Johnson',
                                     'valid_for': ['1']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('User info updated: jack', response.content.decode())
        test_jack = TestUser.objects.get(username="jack")
        self.assertEqual(test_jack.password, hashlib.sha256("word".encode('utf-8')).hexdigest())
