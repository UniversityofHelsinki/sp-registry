from io import StringIO
from unittest.mock import call, patch

from django.core.management import call_command
from django.test import RequestFactory, TestCase

from rr.models.serviceprovider import ServiceProvider


class RemoveServerNameTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.server_names = "ldap.example.org\nldap2.example.org\nldap3.example.org"
        self.sp = ServiceProvider.objects.create(
            entity_id="ldapentity",
            service_type="ldap",
            server_names=self.server_names,
        )
        self.sp2 = ServiceProvider.objects.create(
            entity_id="ldapentity2",
            service_type="ldap",
            server_names="ldap3.example.org",
        )

    def test_remove_server_names_list_only(self):
        out = StringIO()
        call_command("removeservername", "-l", "--host", "ldap2.example.org", stdout=out)
        self.assertEqual(ServiceProvider.objects.get(pk=self.sp.pk).server_names, self.server_names)
        self.assertIn("(List only)", out.getvalue())

    @patch("rr.management.commands.removeservername.logger")
    def test_remove_server_names_remove(self, mock_logger):
        out = StringIO()
        call_command("removeservername", "--host", "ldap2.example.org", stdout=out)
        self.assertEqual(
            ServiceProvider.objects.get(pk=self.sp.pk).server_names, "ldap.example.org\nldap3.example.org"
        )
        mock_logger.info.assert_called_with("Removing server name: ldap2.example.org from service provider ldapentity")

    @patch("rr.management.commands.removeservername.logger")
    def test_remove_server_names_remove_mulitple(self, mock_logger):
        out = StringIO()
        call_command("removeservername", "--host", "ldap2.example.org", "--host", "ldap3.example.org", stdout=out)
        self.assertEqual(ServiceProvider.objects.get(pk=self.sp.pk).server_names, "ldap.example.org")
        self.assertEqual(ServiceProvider.objects.get(pk=self.sp2.pk).server_names, "")
        mock_logger.info.assert_has_calls(
            [
                call("Removing server name: ldap2.example.org from service provider ldapentity"),
                call("Removing server name: ldap3.example.org from service provider ldapentity"),
                call("Removing server name: ldap3.example.org from service provider ldapentity2"),
            ]
        )
