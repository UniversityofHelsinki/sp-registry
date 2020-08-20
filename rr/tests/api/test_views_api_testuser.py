import hashlib

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIRequestFactory

from rr.models.attribute import Attribute
from rr.models.testuser import TestUser, TestUserData
from rr.models.serviceprovider import ServiceProvider
from rr.tests.api.api_common import APITestCase
from rr.views_api.testuser import TestUserViewSet, TestUserDataViewSet


class TestuserTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.saml_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml', test=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:2', service_type='saml', test=True)
        self.saml_sp.admins.add(self.user)
        self.object = TestUser.objects.create(sp=self.saml_sp, username="jack", password="secret", firstname="Jack",
                                              lastname="Tester")
        self.admin_object = TestUser.objects.create(sp=self.admin_sp, username="adminjack", password="adminsecret",
                                                    firstname="Jack", lastname="Admin")
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
                                                  public_oidc=True,
                                                  scoped=True)
        self.data = {'id': self.object.id,
                     'sp': self.object.sp.id,
                     'username': self.object.username,
                     'firstname': self.object.firstname,
                     'lastname': self.object.lastname}
        self.create_data = {'sp': self.object.sp.id,
                            'username': 'newuser',
                            'password': 'newpassword',
                            'firstname': 'Ex',
                            'lastname': 'Org'}
        self.url = '/api/v1/contacts/'
        self.viewset = TestUserViewSet
        self.model = TestUser

    def test_testuser_access_list_without_user(self):
        response = self._test_list(user=None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_testuser_access_list_with_normal_user(self):
        response = self._test_list(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_testuser_access_list_with_superuser(self):
        response = self._test_list(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_testuser_access_object_without_user(self):
        response = self._test_access(user=None, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_testuser_access_object_with_normal_user(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_testuser_access_object_with_normal_user_without_permission(self):
        response = self._test_access(user=self.user, pk=self.admin_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_testuser_access_object_with_superuser(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_testuser_create_with_user(self):
        response = self._test_create(user=self.user, data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.create_data:
            if key != 'password':
                self.assertEqual(response.data[key], self.create_data[key])
        password = hashlib.sha256('newpassword'.encode('utf-8')).hexdigest()
        self.assertEqual(TestUser.objects.get(id=response.data['id']).password, password)

    def test_testuser_delete_with_user(self):
        response = self._test_delete(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNotNone(TestUser.objects.get(pk=self.object.pk).end_at)

    def test_testuser_delete_with_user_without_permission(self):
        response = self._test_delete(user=self.user, pk=self.admin_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_testuser_create_user_with_attributes(self):
        data = self.create_data
        data['attributes'] = [{'attribute': 'eduPersonPrincipalName',
                               'value': 'exorg@example.org'},
                              {'attribute': 'cn',
                               'value': 'Ogre'}]
        response = self._test_create(user=self.user, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.create_data:
            if key != 'password':
                if type(response.data[key]) != list:
                    self.assertEqual(response.data[key], data[key])
                else:
                    self.assertEqual(len(response.data[key]), len(data[key]))

    def test_testuser_remove_attributes(self):
        TestUserData.objects.create(user=self.object, attribute=self.attr_eppn, value='exorg@example.org')
        TestUserData.objects.create(user=self.object, attribute=self.attr_cn, value='Ogre')
        self.assertEqual(len(self.object.attributes.all()), 2)
        data = {
            'id': self.object.pk,
            'attributes': [
                {'attribute': 'eduPersonPrincipalName',
                 'value': 'exorg@example.org'},
                {'attribute': 'cn',
                 'value': ''}]
        }
        response = self._test_patch(user=self.user, data=data, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.object.attributes.all()), 1)

    def test_testuser_create_user_with_valid_for_without_permission(self):
        data = self.create_data
        data['valid_for'] = ['test:entity:1',
                             'test:entity:2']
        response = self._test_create(user=self.user, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_testuser_create_user_with_valid_for_with_permission(self):
        data = self.create_data
        data['valid_for'] = ['test:entity:1',
                             'test:entity:2']
        response = self._test_create(user=self.superuser, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['valid_for']), 2)

    def _initialize_test_user_data(self):
        TestUserData.objects.create(user=self.object, attribute=self.attr_eppn, value='jack@example.org')
        TestUserData.objects.create(user=self.admin_object, attribute=self.attr_eppn, value='adminjack@example.org')
        TestUserData.objects.create(user=self.admin_object, attribute=self.attr_cn, value='Admin')
        self.viewset = TestUserDataViewSet

    def test_testuserdata_access_list_with_normal_user(self):
        self._initialize_test_user_data()
        response = self._test_list(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_testuserdata_access_list_with_superuser(self):
        self._initialize_test_user_data()
        response = self._test_list(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_testuserdata_create_with_user(self):
        self._initialize_test_user_data()
        data = {'user': self.object.pk,
                'attribute': 'cn',
                'value': 'Jack'}
        response = self._test_create(user=self.user, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(self.object.attributes.all()), 2)

    def test_testuserdata_delete_with_user(self):
        data = TestUserData.objects.create(user=self.object, attribute=self.attr_eppn, value='jack@example.org')
        self.viewset = TestUserDataViewSet
        response = self._test_delete(user=self.user, pk=data.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(self.object.attributes.all()), 0)

    def test_testuserdata_delete_with_user_without_permission(self):
        data = TestUserData.objects.create(user=self.admin_object, attribute=self.attr_cn, value='Admin')
        self.viewset = TestUserDataViewSet
        response = self._test_delete(user=self.user, pk=data.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
