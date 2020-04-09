from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.serviceprovider import ServiceProvider


class ServiceProviderSAMLTechnicalTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_sp_technical_view_denies_anonymous(self):
        response = self.client.get(reverse('technical-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('technical-update', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('technical-update', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('technical-update', kwargs={'pk': self.user_sp.pk}))

    def test_sp_technical_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('technical-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('technical-update', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_sp_technical_view_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('technical-update', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_sp_technical_entity_id_change(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'entity_id': 'invalid_entity_id'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Entity Id should be URI', response.content.decode())
        response = self.client.post(reverse('technical-update', kwargs={'pk': self.user_sp.pk}),
                                    {'entity_id': 'https://valid.entity.id'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Entity Id should be URI', response.content.decode())
        self.assertIn('https://valid.entity.id', response.content.decode())

    def test_sp_technical_view_production_disabled_if_missing(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('technical-update', kwargs={'pk': self.user_sp.pk}))
        self.assertIn('name="production" disabled', response.content.decode())

    def test_sp_technical_view_production_not_disabled_with_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('technical-update', kwargs={'pk': self.user_sp.pk}))
        self.assertNotIn('name="production" disabled', response.content.decode())
