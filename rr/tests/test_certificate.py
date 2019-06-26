from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from rr.forms.certificate import CertificateForm
from rr.models.certificate import Certificate
from rr.models.serviceprovider import ServiceProvider
from rr.views.certificate import certificate_list


class CertificateFormTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='tester')
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.admin_sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml')
        self.user_sp = ServiceProvider.objects.create(entity_id='https://sp2.example.org/sp', service_type='saml')
        self.user_sp.admins.add(self.user)
        self.invalid_certificate = """MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
BAMMDnNwLmV4YW1wbGUub3JnMB4XDTE4MDExNjExMTAxN1oXDTI4MDExNDExMTAx
N1owGTEXMBUGA1UEAwwOc3AuZXhhbXBsZS5vcmcwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDlomqiyCbu1nKL9BtTwFjuNr0O2iDrQ1DbOnMu6E3tg0CO
kvmxzy7e9RuVzJUzz4bCz5u7xoHAFzaOX/k0FwRp32k9//4KNiioZta+sOE5ewyi
9ooOxqYtBMC7xy4AF/+7U2XoeGvdPPswUjEB0b312K4Xu3tvQy4ZdDhIiIHizLng
bHOUX8Isq50z8PmSEPE/DMMfK4mvfSMT067fC6tX+WHjlb8PHgEBn09f8kL76+x6
JLm6uGPN2M0lL1mtoN3lumYxldifsf2REuZdVSQYGRqQWjvMDJCPy1NRyvUHRDRr
FWIgEJhSpp0PdLd+9oK4Wccw8L2PN/khpXAJAVrAuMrOzASWL+ZuCQbUHSoK0Asb
4eN5jgDBNU63P/Ev4//JaUwNmYWMSeqEEKzun0WansZFC2LUkVjvuSZ2JV4bzu+s
pRdj0dkEa5HOhk7Bvd/eN0h2aVLsF3EgXekDudbKXMwQOxrazJoVHv9pwxsZxlHK
LP298175K/skR8VASQdH3JBrXpdiDb4mLoyXdx/I11Tx13fuiQogIRcm6ccqy/Ob
1nFzh1tkqTaFJF2F3cLCpbrqv853vWC08bRACkIeJQ8R8EDJudvk3cQllHHfItss
yoR//TcHJXsu+zwTruW6wdLkXShG3v2N2zplChuUczFYOT1FjZa+hRhk8p6tOwID
AQABo1AwTjAdBgNVHQ4EFgQU2TjrYXoZH0JkPA3YIZe+H0v1jqcwHwYDVR0jBBgw
FoAU2TjrYXoZH0JkPA3YIZe+H0v1jqcwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAgEAJUjWKsLdtVI5xqfi7RLk1viyTdvKi2sTkXgKySNPffwRLoEcmIAp
FPX0TAhsoBdxE7OFwlSmb6ZX89CtNlwyyVHlWemwgKNfjdgj0qkk7Lreq+L1si6j
diml6uFfMbZrHtppxHENDYckxxfD3Zooa/pY9NUG17BHzoNTAsDhFq7YCA4Y2j6h
acYh1pa0PQ4rhE2zhFs3AZF+gaYGdwtKEcJBEQ6OcctP3Y8K/FTDmJAK3dERdmrh
BdeYSRTQSQMm0W1SsIsEMEfndC1Cca/aKrl8B1tZz55s04WPx/e92NV9S5KGRH0G
UADycvLo12NUfqubK+2+bcH92rhHZ1QGjkfJmHwhXIqt8F1gysQQO+M3uYhlpiIR
4vQBWFqoMCT7lqQYj1tCvrt6+RVv3Zz8t0eMfJXSFAoJPbjv3npPcUfjmLRG7W9y
VSb6gzk3PYRVB0NzmlPdB4KFdBQbsuE8qoPr3UBbHIiD9wFU6K6eUZkIjqIV/5az
56c2mntFDpdx+46RkS/7CEAbZkD8kEM5vrhpDXhbfLzIDTnOTBTbrwGmPCnpYSXy
rKLt+NcwtbkI6weLISJu9lFZnPMYT7LpqDWD4aMHHUWr8THO0T6mbCeQRYMlfSpU
0es8zIhYt2fRbxHFRIFyRZYJrQoSfkU5OMas/ypz/q2wOvgqjH8qyRQ
"""

        self.valid_certificate = """MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
BAMMDnNwLmV4YW1wbGUub3JnMB4XDTE4MDExNjExMTAxN1oXDTI4MDExNDExMTAx
N1owGTEXMBUGA1UEAwwOc3AuZXhhbXBsZS5vcmcwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDlomqiyCbu1nKL9BtTwFjuNr0O2iDrQ1DbOnMu6E3tg0CO
kvmxzy7e9RuVzJUzz4bCz5u7xoHAFzaOX/k0FwRp32k9//4KNiioZta+sOE5ewyi
9ooOxqYtBMC7xy4AF/+7U2XoeGvdPPswUjEB0b312K4Xu3tvQy4ZdDhIiIHizLng
bHOUX8Isq50z8PmSEPE/DMMfK4mvfSMT067fC6tX+WHjlb8PHgEBn09f8kL76+x6
JLm6uGPN2M0lL1mtoN3lumYxldifsf2REuZdVSQYGRqQWjvMDJCPy1NRyvUHRDRr
FWIgEJhSpp0PdLd+9oK4Wccw8L2PN/khpXAJAVrAuMrOzASWL+ZuCQbUHSoK0Asb
4eN5jgDBNU63P/Ev4//JaUwNmYWMSeqEEKzun0WansZFC2LUkVjvuSZ2JV4bzu+s
pRdj0dkEa5HOhk7Bvd/eN0h2aVLsF3EgXekDudbKXMwQOxrazJoVHv9pwxsZxlHK
LP298175K/skR8VASQdH3JBrXpdiDb4mLoyXdx/I11Tx13fuiQogIRcm6ccqy/Ob
1nFzh1tkqTaFJF2F3cLCpbrqv853vWC08bRACkIeJQ8R8EDJudvk3cQllHHfItss
yoR//TcHJXsu+zwTruW6wdLkXShG3v2N2zplChuUczFYOT1FjZa+hRhk8p6tOwID
AQABo1AwTjAdBgNVHQ4EFgQU2TjrYXoZH0JkPA3YIZe+H0v1jqcwHwYDVR0jBBgw
FoAU2TjrYXoZH0JkPA3YIZe+H0v1jqcwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAgEAJUjWKsLdtVI5xqfi7RLk1viyTdvKi2sTkXgKySNPffwRLoEcmIAp
FPX0TAhsoBdxE7OFwlSmb6ZX89CtNlwyyVHlWemwgKNfjdgj0qkk7Lreq+L1si6j
diml6uFfMbZrHtppxHENDYckxxfD3Zooa/pY9NUG17BHzoNTAsDhFq7YCA4Y2j6h
acYh1pa0PQ4rhE2zhFs3AZF+gaYGdwtKEcJBEQ6OcctP3Y8K/FTDmJAK3dERdmrh
BdeYSRTQSQMm0W1SsIsEMEfndC1Cca/aKrl8B1tZz55s04WPx/e92NV9S5KGRH0G
UADycvLo12NUfqubK+2+bcH92rhHZ1QGjkfJmHwhXIqt8F1gysQQO+M3uYhlpiIR
4vQBWFqoMCT7lqQYj1tCvrt6+RVv3Zz8t0eMfJXSFAoJPbjv3npPcUfjmLRG7W9y
VSb6gzk3PYRVB0NzmlPdB4KFdBQbsuE8qoPr3UBbHIiD9wFU6K6eUZkIjqIV/5az
56c2mntFDpdx+46RkS/7CEAbZkD8kEM5vrhpDXhbfLzIDTnOTBTbrwGmPCnpYSXy
rKLt+NcwtbkI6weLISJu9lFZnPMYT7LpqDWD4aMHHUWr8THO0T6mbCeQRYMlfSpU
0es8zIhYt2fRbxHFRIFyRZYJrQoSfkU5OMas/ypz/q2wOvgqjH8qyRQ=
"""

    def test_certificate_form_save_content_saml_user(self):
        form_data = {'certificate': self.valid_certificate, 'encryption': True, 'signing': True}
        form = CertificateForm(sp=self.user_sp, data=form_data)
        self.assertTrue(form.is_valid())

    def test_certificate_form_save_invalid_content_saml_user(self):
        form_data = {'certificate': self.invalid_certificate, 'encryption': True, 'signing': True}
        form = CertificateForm(sp=self.user_sp, data=form_data)
        self.assertFalse(form.is_valid())

    def test_certificate_view_denies_anonymous(self):
        response = self.client.get(reverse('certificate-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('certificate-list', kwargs={'pk': self.user_sp.pk}))
        response = self.client.post(reverse('certificate-list', kwargs={'pk': self.user_sp.pk}), follow=True)
        self.assertRedirects(response,
                             reverse('login') + '?next=' + reverse('certificate-list', kwargs={'pk': self.user_sp.pk}))

    def test_certificate_view_denies_unauthorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('certificate-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('certificate-list', kwargs={'pk': self.admin_sp.pk}))
        self.assertEqual(response.status_code, 404)

    def test_certificate_view_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('certificate-list', kwargs={'pk': self.user_sp.pk}))
        self.assertEqual(response.status_code, 200)

    def test_certificate_form_view_add_certificate(self):
        form_data = {'certificate': self.valid_certificate, 'encryption': True, 'signing': True, 'add_cert': True}
        request = self.factory.post(reverse('certificate-list', kwargs={'pk': self.user_sp.pk}), form_data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = certificate_list(request, pk=self.user_sp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Certificate.objects.filter(sp=self.user_sp).count(), 1)
