from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.models.contact import Contact
from rr.models.serviceprovider import ServiceProvider


class ContactTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_contact_view_denies_anonymous(self):
        response = self.client.get(reverse('contact-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('contact-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('contact-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('contact-list', kwargs={'pk': self.user_sp.pk}))

    def test_contact_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('contact-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('contact-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_contact_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('contact-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_post_add_contact(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('contact-list', kwargs={'pk': self.user_sp.pk}),
                                    {'add_contact': 'ok',
                                     'type': 'technical',
                                     'firstname': 'John',
                                     'lastname': 'Johnson',
                                     'email': 'john@example.org'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('john@example.org', response.content.decode())
        self.assertEqual(Contact.objects.filter(sp=self.user_sp).count(), 1)
