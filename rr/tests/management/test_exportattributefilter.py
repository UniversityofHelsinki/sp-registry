import os
from io import StringIO

from django.core.management import call_command
from django.test import RequestFactory, TestCase

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute

VALID_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<AttributeFilterPolicyGroup xmlns="urn:mace:shibboleth:2.0:afp" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="urn:mace:funet.fi:haka" xmlns:basic="urn:mace:shibboleth:2.0:afp:mf:basic" xmlns:saml="urn:mace:shibboleth:2.0:afp:mf:saml" xsi:schemaLocation="urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd urn:mace:shibboleth:2.0:afp:mf:basic classpath:/schema/shibboleth-2.0-afp-mf-basic.xsd urn:mace:shibboleth:2.0:afp:mf:saml classpath:/schema/shibboleth-2.0-afp-mf-saml.xsd">
  <AttributeFilterPolicy id="hy-default-test:entity:1">
    <PolicyRequirementRule value="test:entity:1" xsi:type="basic:AttributeRequesterString"/>
    <AttributeRule attributeID="id-urn:mace:dir:attribute-def:eduPersonPrincipalName">
      <PermitValueRule xsi:type="basic:ANY"/>
    </AttributeRule>
    <AttributeRule attributeID="id-urn:mace:terena.org:schac:attribute-def:schacPersonalUniqueID">
      <PermitValueRule xsi:type="basic:ANY"/>
    </AttributeRule>
  </AttributeFilterPolicy>
</AttributeFilterPolicyGroup>
"""


class ExportMetadataTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sp = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml', production=True)
        self.attr_eppn = Attribute.objects.create(friendlyname='eduPersonPrincipalName',
                                                  name='urn:oid:1.3.6.1.4.1.5923.1.1.1.6',
                                                  attributeid='id-urn:mace:dir:attribute-def:eduPersonPrincipalName',
                                                  nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                                  public_saml=True,
                                                  public_ldap=False)
        self.attr_uniqueid = Attribute.objects.create(friendlyname='schacPersonalUniqueID',
                                        name='urn:oid:1.3.6.1.4.1.25178.1.2.15',
                                        attributeid='id-urn:mace:terena.org:schac:attribute-def:schacPersonalUniqueID',
                                        nameformat='urn:oasis:names:tc:SAML:2.0:attrname-format:uri',
                                        public_saml=False,
                                        public_ldap=False)
        SPAttribute.objects.create(attribute=self.attr_eppn, sp=self.sp, reason='User identification')
        SPAttribute.objects.create(attribute=self.attr_uniqueid, sp=self.sp, reason='User identification')

    def test_exportmetadata(self):
        out = StringIO()
        call_command('exportattributefilter', '-p', '-u', stdout=out)
        self.assertEqual(VALID_DATA, out.getvalue())
