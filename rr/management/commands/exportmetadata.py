"""
Command line script for exporting metadata

Usage help: ./manage.py cleandb -h
"""

from lxml import etree, objectify
from django.core.management.base import BaseCommand
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.utils.metadata_generator import metadata_spssodescriptor, metadata_contact,\
    metadata_organization, get_service_providers, metadata_generator_list


def attributefilter_generate(element, sp, validated=True):
    """
    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    if validated:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
    if attributes:
        AttributeFilterPolicy = etree.SubElement(element, "AttributeFilterPolicy", id="hy-default-" + sp.entity_id)
        PolicyRequirementRule = etree.SubElement(AttributeFilterPolicy, "PolicyRequirementRule", value=sp.entity_id)
        PolicyRequirementRule.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "basic:AttributeRequesterString"
        for attribute in attributes:
            AttributeRule = etree.SubElement(AttributeFilterPolicy, "AttributeRule", attributeID=attribute.attribute.attributeid)
            PermitValueRule = etree.SubElement(AttributeRule, "PermitValueRule")
            PermitValueRule.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "basic:ANY"


class Command(BaseCommand):
    help = 'Exports validated metadata'

    def add_arguments(self, parser):
        parser.add_argument('-p', action='store_true', dest='production', help='Include production service providers')
        parser.add_argument('-t', action='store_true', dest='test', help='Include test service providers')
        parser.add_argument('-m', type=str, action='store', dest='metadata', help='Metadata output file name')
        parser.add_argument('-a', type=str, action='store', dest='attributefilter', help='Attribute filter output file name')
        parser.add_argument('-i', type=str,  nargs='+', action='store', dest='include', help='List of included entityIDs')
        parser.add_argument('-u', action='store_true', dest='unvalidated', help='Use unvalidated data')
        parser.add_argument('-x', action='store_true', dest='privacypolicy', help='Replace missing privacypolicy for HY')

    def handle(self, *args, **options):
        production = options['production']
        test = options['test']
        metadata_output = options['metadata']
        attributefilter_output = options['attributefilter']
        include = options['include']
        validated = not options['unvalidated']
        privacypolicy = options['privacypolicy']
        if not production and not test and not include:
            self.stdout.write("Give production, test or included entityIDs as command line arguments")
        serviceproviders = get_service_providers(validated, production, test, include)
        # Create XML containing selected EntityDescriptors
        if serviceproviders:
            if metadata_output:
                metadata = metadata_generator_list(serviceproviders, validated, privacypolicy)
                with open(metadata_output, 'wb') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                    # Hack for correcting namespace definition by removing prefix.
                    f.write(etree.tostring(metadata, pretty_print=True, encoding='UTF-8').replace(b'xmlns:xmlns', b'xmlns'))
            if attributefilter_output:
                attributefilter = etree.Element("AttributeFilterPolicyGroup", id="urn:mace:funet.fi:haka", nsmap={"xmlns": 'urn:mace:shibboleth:2.0:afp'})
                attributefilter.attrib['{urn:mace:shibboleth:2.0:afp}basic'] = "urn:mace:shibboleth:2.0:afp:mf:basic"
                attributefilter.attrib['{urn:mace:shibboleth:2.0:afp}saml'] = "urn:mace:shibboleth:2.0:afp:mf:saml"
                attributefilter.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = "urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd urn:mace:shibboleth:2.0:afp:mf:basic classpath:/schema/shibboleth-2.0-afp-mf-basic.xsd urn:mace:shibboleth:2.0:afp:mf:saml classpath:/schema/shibboleth-2.0-afp-mf-saml.xsd"
                for sp in serviceproviders:
                    attributefilter_generate(attributefilter, sp, validated)
                with open(attributefilter_output, 'wb') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                    # Hack for correcting namespace definition by removing prefix.
                    f.write(etree.tostring(attributefilter, pretty_print=True, encoding='UTF-8').replace(b'xmlns:xmlns', b'xmlns'))
