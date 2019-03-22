from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from rr.models.serviceprovider import ServiceProvider
from rr.views.serviceprovider import ServiceProviderList


class ServiceProviderListTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_sp_list_anonymous_user(self):
        c = Client()
        response = c.get(reverse('serviceprovider-list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], reverse('login') + '?next=/list/')

    def test_sp_list_normal_user(self):
        request = self.factory.get(reverse('serviceprovider-list'))
        request.user = self.user
        response = ServiceProviderList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.admin_sp not in response.context_data['object_list'])
        self.assertTrue(self.user_sp in response.context_data['object_list'])

    def test_sp_list_super_user(self):
        request = self.factory.get(reverse('serviceprovider-list'))
        request.user = self.superuser
        response = ServiceProviderList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.admin_sp in response.context_data['object_list'])
        self.assertTrue(self.user_sp in response.context_data['object_list'])
