import json
from io import StringIO

from django.core.management import call_command
from django.test import RequestFactory, TestCase

from rr.models.serviceprovider import ServiceProvider


class ExportOIDCMetadataTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_sp = ServiceProvider.objects.create(
            entity_id="https://sp2.example.org/sp",
            service_type="oidc",
            name_en="SP2 Example service",
            privacypolicy_fi="https://example.org/privacyfi",
            production=True,
        )

    def test_exportoidcmetadata(self):
        out = StringIO()
        call_command("exportoidc", "-p", "-u", stdout=out)
        self.assertIn('"client_id": "https://sp2.example.org/sp"', out.getvalue())
        self.assertTrue(len(json.loads(out.getvalue())) == 1)
        self.assertTrue(len(json.loads(out.getvalue())[0]) == 6)
