from django.contrib.auth.models import Group, User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from rr.models.certificate import Certificate
from rr.models.serviceprovider import ServiceProvider
from rr.tests.api.api_common import APITestCase
from rr.views_api.certificate import CertificateViewSet


class CertificateTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username="tester")
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.user_sp = ServiceProvider.objects.create(
            entity_id="https://sp2.example.org/sp", service_type="saml", name_en="My Test"
        )
        self.user_sp.admins.add(self.user)
        self.admin_sp = ServiceProvider.objects.create(entity_id="test:entity:1", service_type="saml")

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
        self.object = Certificate.objects.add_certificate(
            certificate=self.valid_certificate, sp=self.user_sp, encryption=False, signing=True
        )
        self.superuser_object = Certificate.objects.add_certificate(
            certificate=self.valid_certificate, sp=self.admin_sp, encryption=False, signing=False
        )
        self.data = {
            "id": self.object.id,
            "sp": self.object.sp.id,
            "certificate": self.object.certificate,
            "signing": self.object.signing,
            "encryption": self.object.encryption,
        }
        self.create_data = {
            "sp": self.object.sp.id,
            "certificate": self.valid_certificate,
            "signing": True,
            "encryption": True,
        }
        self.create_error_data = {
            "sp": self.object.sp.id,
            "certificate": self.valid_certificate[:-20],
            "signing": True,
            "encryption": True,
        }
        self.url = "/api/v1/certificates/"
        self.viewset = CertificateViewSet
        self.model = Certificate

    def test_certificate_access_list_without_user(self):
        response = self._test_list(user=None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_certificate_access_list_with_normal_user(self):
        response = self._test_list(user=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_certificate_access_list_with_superuser(self):
        response = self._test_list(user=self.superuser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_certificate_access_object_without_user(self):
        response = self._test_access(user=None, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_certificate_access_object_with_normal_user(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_certificate_access_object_with_normal_user_without_permission(self):
        response = self._test_access(user=self.user, pk=self.superuser_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(READ_ALL_GROUP="read_all")
    def test_certificate_access_object_with_read_all_permission(self):
        group = Group.objects.create(name="read_all")
        group.user_set.add(self.user)
        response = self._test_access(user=self.user, pk=self.superuser_object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_certificate_access_object_with_superuser(self):
        response = self._test_access(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in self.data:
            self.assertEqual(response.data[key], self.data[key])

    def test_certificate_create_with_user(self):
        response = self._test_create(user=self.user, data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.create_data:
            self.assertEqual(response.data[key], self.create_data[key])

    def test_certificate_create_error_with_user(self):
        response = self._test_create(user=self.user, data=self.create_error_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_certificate_delete_with_user(self):
        response = self._test_delete(user=self.user, pk=self.object.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNotNone(Certificate.objects.get(pk=self.object.pk).end_at)

    def test_certificate_delete_with_user_without_permission(self):
        response = self._test_delete(user=self.user, pk=self.superuser_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
