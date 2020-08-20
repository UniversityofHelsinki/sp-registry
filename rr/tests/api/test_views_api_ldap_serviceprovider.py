from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APIRequestFactory

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider
from rr.tests.api.api_common import APITestCase
from rr.views_api.serviceprovider import LdapServiceProviderViewSet


class ServiceTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username='superuser', is_superuser=True)
        self.object = ServiceProvider.objects.create(service_type='ldap',
                                                     name_fi='My Test LDAP')
        self.object.admins.add(self.user)
        self.super_user_object = ServiceProvider.objects.create(name_fi='Admin LDAP', service_type='ldap')
        self.data = {'id': self.object.id,
                     'name_fi': self.object.name_fi}
        self.create_data = {'name_fi': 'New LDAP Service'}
        self.update_data = {'id': self.object.id, 'name_fi': 'Your test'}
        self.url = '/api/v1/services/ldap/'
        self.viewset = LdapServiceProviderViewSet
        self.model = ServiceProvider

    def test_service_provider_access_list_without_user(self):
        response = self._test_list(user=None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_service_provider_access_list_with_normal_user(self):
        response = self._test_list(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_service_provider_access_list_with_superuser(self):
        response = self._test_list(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_service_provider_access_object_without_user(self):
        response = self._test_access(user=None, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_service_provider_access_object_with_normal_user(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_service_provider_access_object_with_normal_user_without_permission(self):
        response = self._test_access(user=self.user, pk=self.super_user_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_service_provider_access_object_with_superuser(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_service_provider_update_with_normal_user(self):
        response = self._test_update(user=self.user, data=self.update_data, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.update_data:
            self.assertEqual(response.data[key], self.update_data[key])

    def test_service_provider_update_with_normal_user_without_permission(self):
        response = self._test_update(user=self.user, data=self.update_data, pk=self.super_user_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_service_provider_update_with_superuser(self):
        response = self._test_update(user=self.superuser, data=self.update_data, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.update_data:
            self.assertEqual(response.data[key], self.update_data[key])

    def test_service_provider_create_with_user(self):
        response = self._test_create(user=self.user, data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.create_data:
            self.assertEqual(response.data[key], self.create_data[key])
        self.assertEqual(response.data['admins'], [self.user.username])

    def test_service_provider_create_with_nested_data(self):
        Group.objects.create(name="TestGroup")
        self.attr_cn = Attribute.objects.create(friendlyname='cn',
                                                name='urn:oid:2.5.4.3',
                                                attributeid='id-urn:mace:dir:attribute-def:cn',
                                                nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                public_ldap=True)
        self.attr_eppn = Attribute.objects.create(friendlyname='eduPersonPrincipalName',
                                                  name='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                                                  attributeid='id-urn:mace:dir:attribute-def:eduPersonPrincipalName',
                                                  nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                  public_ldap=True)
        data = {'name_fi': 'Created LDAP provider',
                'admins': ['superuser', 'tester'],
                'admin_groups': ['TestGroup'],
                'contacts': [{'type': 'technical', 'firstname': 'Test', 'lastname': 'User', 'email': 'tester@example.org'},
                             {'type': 'administrative', 'firstname': 'Foo', 'lastname': 'Bar', 'email': 'foo.bar@example.org'}],
                'attributes': [{'attribute': 'eduPersonPrincipalName', 'reason': 'User Identification'}]
                }
        response = self._test_create(user=self.user, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sp_id = response.data['id']
        for key in data:
            if type(response.data[key]) != list:
                self.assertEqual(response.data[key], data[key])
            else:
                self.assertEqual(len(response.data[key]), len(data[key]))

    def test_service_provider_update_with_nested_data(self):
        self.test_service_provider_create_with_nested_data()
        data = {'name_en': 'Changed provider',
                'contacts': [{'type': 'technical', 'firstname': 'Test', 'lastname': 'User', 'email': 'tester@example.org'},
                             {'type': 'support', 'firstname': 'Mr.', 'lastname': 'Frog', 'email': 'mr.frog@example.org'}],
                'attributes': [{'attribute': 'cn', 'reason': 'Frog'},
                               {'attribute': 'eduPersonPrincipalName', 'reason': 'Identification'}]
                }
        response = self._test_update(user=self.user, data=data, pk=self.sp_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['attributes']), 2)
        self.assertEqual(len(response.data['contacts']), 2)

    def test_service_provider_update_with_nested_attribute_Removal(self):
        self.test_service_provider_create_with_nested_data()
        data = {'attributes': [{'attribute': 'cn', 'reason': 'Frog'}]}
        response = self._test_update(user=self.user, data=data, pk=self.sp_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['attributes']), 1)

    def test_service_provider_delete_with_user(self):
        response = self._test_delete(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNotNone(ServiceProvider.objects.get(pk=self.object.pk).end_at)
