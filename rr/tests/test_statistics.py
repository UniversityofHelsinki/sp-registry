from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.statistics import Statistics
from rr.models.serviceprovider import ServiceProvider


class StatisticsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)
        Statistics.objects.create(sp=self.user_sp, date=date.today() - timedelta(days=1), logins=1561)
        Statistics.objects.create(sp=self.user_sp, date=date.today() - timedelta(days=2), logins=124)
        Statistics.objects.create(sp=self.user_sp, date=date.today() - timedelta(days=33), logins=3356)

    def test_statistics_view_denies_anonymous(self):
        response = self.client.get(reverse('statistics-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('statistics-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('statistics-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('statistics-list', kwargs={'pk': self.user_sp.pk}))

    def test_statistics_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('statistics-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('statistics-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_statistics_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('statistics-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('1561', response.content.decode())
        self.assertNotIn('3356', response.content.decode())
