from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIRequestFactory

from rr.models.redirecturi import RedirectUri
from rr.models.serviceprovider import ServiceProvider
from rr.tests.api.api_common import APITestCase
from rr.views_api.redirecturi import RedirectUriViewSet


class RedirectUriTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.user_sp = ServiceProvider.objects.create(
            entity_id="https://sp2.example.org/sp",
            service_type="oidc",
            name_en="SP2 Example service",
        )
        self.admin_sp = ServiceProvider.objects.create(entity_id="test:entity:1", service_type="oidc")
        self.user_sp.admins.add(self.user)
        self.object = RedirectUri.objects.create(sp=self.user_sp, uri="https://sp2.example.org/")
        self.superuser_object = RedirectUri.objects.create(sp=self.admin_sp, uri="https://sp.example.org/")
        self.data = {"id": self.object.id, "sp": self.object.sp.id, "uri": self.object.uri}
        self.create_data = {"sp": self.object.sp.id, "uri": "https://sp2.example.org/redirect"}
        self.create_error_data = {"id": self.object.id, "uri": "invalid"}
        self.url = "/api/v1/redirecturis/"
        self.viewset = RedirectUriViewSet
        self.model = RedirectUri

    def test_redirecturi_access_list_without_user(self):
        response = self._test_list(user=None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_redirecturi_access_list_with_normal_user(self):
        response = self._test_list(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_redirecturi_access_list_with_superuser(self):
        response = self._test_list(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_redirecturi_access_object_without_user(self):
        response = self._test_access(user=None, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_redirecturi_access_object_with_normal_user(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_redirecturi_access_object_with_normal_user_without_permission(self):
        response = self._test_access(user=self.user, pk=self.superuser_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_redirecturi_access_object_with_superuser(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_redirecturi_create_with_user(self):
        response = self._test_create(user=self.user, data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.create_data:
            self.assertEqual(response.data[key], self.create_data[key])

    def test_redirecturi_create_error_with_user(self):
        response = self._test_create(user=self.user, data=self.create_error_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_redirecturi_delete_with_user(self):
        response = self._test_delete(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNotNone(RedirectUri.objects.get(pk=self.object.pk).end_at)

    def test_redirecturi_delete_with_user_without_permission(self):
        response = self._test_delete(user=self.user, pk=self.superuser_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
