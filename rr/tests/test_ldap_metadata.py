import os

from datetime import datetime, timezone
from io import StringIO
from lxml import etree

from django.core.management import call_command
from django.test import TestCase

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.usergroup import UserGroup
from rr.utils.ldap_metadata_generator import ldap_metadata_generator_list

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/ldap_metadata.xml')


class LdapMetadataTestCase(TestCase):
    def setUp(self):
        validation_time = datetime.strptime('20190102 12:01:02', '%Y%m%d %H:%M:%S').astimezone(timezone.utc)
        self.sp = ServiceProvider.objects.create(entity_id='ldaptestservice', service_type='ldap',
                                                 production=True, target_group='restricted', service_account=True,
                                                 service_account_contact='service.user@example.org +358501234567',
                                                 server_names='ldaptest.example.org\nldaptest-2.example.org',
                                                 validated=validation_time)
        attr_cn = Attribute.objects.create(friendlyname='cn',
                                           name='urn:oid:cn',
                                           attributeid='id-cn',
                                           nameformat='urn:uri',
                                           public_ldap=True,
                                           group='name')
        attr_mail = Attribute.objects.create(friendlyname='mail',
                                             name='urn:oid:mail',
                                             attributeid='id-mail',
                                             nameformat='urn:uri',
                                             public_ldap=True)
        UserGroup.objects.create(sp=self.sp, name='grp-gamma', validated=validation_time)
        SPAttribute.objects.create(sp=self.sp, attribute=attr_cn, validated=validation_time)
        SPAttribute.objects.create(sp=self.sp, attribute=attr_mail, validated=validation_time)
        self.test_metadata = open(TESTDATA_FILENAME).read()
        self.maxDiff = None

    def test_ldap_metadata_generation(self):
        metadata_tree = ldap_metadata_generator_list(validated=True, production=True, include=None)
        metadata = etree.tostring(metadata_tree, pretty_print=True,
                                  encoding='UTF-8')
        self.assertEqual(metadata.decode("utf-8"), self.test_metadata)

    def test_exportldap_management_command(self):
        out = StringIO()
        call_command('exportldap', '-p', stdout=out)
        self.assertEqual(out.getvalue(), '<?xml version="1.0" encoding="UTF-8"?>\n' + self.test_metadata)
