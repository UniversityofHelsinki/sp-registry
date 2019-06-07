from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.forms.redirecturi import RedirectUriForm
from rr.models.redirecturi import RedirectUri
from rr.models.serviceprovider import ServiceProvider


class RedirectUriTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='oidc')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='oidc')
        self.user_sp.admins.add(self.user)

    def test_redirect_uri_form_save_correct_content(self):
        form_data = {'uri': 'https://example.org/redirect_uri'}
        form = RedirectUriForm(sp=self.user_sp, data=form_data)
        self.assertTrue(form.is_valid())

    def test_redirect_uri_form_save_duplicate_content(self):
        RedirectUri.objects.create(sp=self.user_sp, uri='https://example.org/redirect_uri')
        form_data = {'uri': 'https://example.org/redirect_uri'}
        form = RedirectUriForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('URI already exists', form.errors['__all__'])

    def test_redirect_uri_form_save_fragment(self):
        form_data = {'uri': 'https://example.org/redirect_uri#2'}
        form = RedirectUriForm(sp=self.user_sp, data=form_data)
        self.assertIn('URIs must not contain fragments', form.errors['__all__'])
        self.assertFalse(form.is_valid())

    def test_redirect_uri_form_save_schema(self):
        form_data = {'uri': 'http://example.org/redirect_uri'}
        self.user_sp.application_type = 'web'
        self.user_sp.save()
        form = RedirectUriForm(sp=self.user_sp, data=form_data)
        self.assertIn('Web application URIs must begin with https: scheme', form.errors['__all__'])
        self.assertFalse(form.is_valid())

    def test_redirect_uri_form_save_not_url(self):
        form_data = {'uri': 'redirect_uri'}
        form = RedirectUriForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Enter a valid URI.', form.errors['__all__'])

    def test_redirect_uri_view_denies_anonymous(self):
        response = self.client.get(reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}))

    def test_redirect_uri_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('redirecturi-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('redirecturi-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_redirect_uri_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_redirect_uri_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('redirecturi-list', kwargs={'pk': self.user_sp.pk}),
                                    {'add_redirecturi': 'ok',
                                     'uri': 'https://example.org/redirect_uri'
                                     })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RedirectUri.objects.filter(sp=self.user_sp).count(), 1)
