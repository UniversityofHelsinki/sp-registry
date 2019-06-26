from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.forms.endpoint import EndpointForm
from rr.models.endpoint import Endpoint
from rr.models.serviceprovider import ServiceProvider


class EndpointTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)

    def test_attribute_form_save_correct_content(self):
        form_data = {'type': 'AssertionConsumerService',
                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     'location': 'https://sp1.example.org/SSO/POST'
                     }
        form = EndpointForm(sp=self.user_sp, data=form_data)
        self.assertTrue(form.is_valid())

    def test_attribute_form_save_duplicate_content(self):
        Endpoint.objects.create(sp=self.user_sp,
                                type='AssertionConsumerService',
                                binding='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                                location='https://sp1.example.org/SSO/POST')
        form_data = {'type': 'AssertionConsumerService',
                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     'location': 'https://sp1.example.org/SSO/POST'
                     }
        form = EndpointForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Endpoint already exists', form.errors['__all__'])

    def test_attribute_form_save_duplicate_index(self):
        Endpoint.objects.create(sp=self.user_sp,
                                type='AssertionConsumerService',
                                binding='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                                location='https://sp1.example.org/SSO/POST',
                                index=1)
        form_data = {'type': 'AssertionConsumerService',
                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     'location': 'https://sp1.example.org/SSO/POST/2',
                     'index': 1
                     }
        form = EndpointForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Index already exists', form.errors['__all__'])

    def test_attribute_form_save_default_without_index(self):
        form_data = {'type': 'AssertionConsumerService',
                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     'location': 'https://sp1.example.org/SSO/POST/2',
                     'is_default': True
                     }
        form = EndpointForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Default endpoint must be indexed', form.errors['__all__'])

    def test_attribute_form_save_duplicate_default(self):
        Endpoint.objects.create(sp=self.user_sp,
                                type='AssertionConsumerService',
                                binding='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                                location='https://sp1.example.org/SSO/POST',
                                is_default=True,
                                index=1)
        form_data = {'type': 'AssertionConsumerService',
                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                     'location': 'https://sp1.example.org/SSO/POST/2',
                     'is_default': True,
                     'index': 2
                     }
        form = EndpointForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Default endpoint already exists', form.errors['__all__'])

    def test_endpoint_view_denies_anonymous(self):
        response = self.client.get(reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}))

    def test_endpoint_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('endpoint-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('endpoint-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_endpoint_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_endpoint_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('endpoint-list', kwargs={'pk': self.user_sp.pk}),
                                    {'add_endpoint': 'ok',
                                     'type': 'AssertionConsumerService',
                                     'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
                                     'location': 'https://sp1.example.org/SSO/POST'
                                     })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Endpoint.objects.filter(sp=self.user_sp).count(), 1)
