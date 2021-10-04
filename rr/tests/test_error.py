from django.test import RequestFactory, TestCase
from django.urls import reverse


class ServiceProviderListTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_generic_error(self):
        response = self.client.get(reverse('error'), {'errorType': 'opensaml::FatalProfileException'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('FatalProfileException', response.content.decode())

    def test_mfa_error(self):
        response = self.client.get(reverse('error'),
                                   {'errorType': 'opensaml::FatalProfileException',
                                    'statusCode2': 'urn:oasis:names:tc:SAML:2.0:status:NoAuthnContext'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your identity provider does not support multi-factor authentication', response.content.decode())
