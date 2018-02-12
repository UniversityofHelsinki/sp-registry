"""
Command line script for exporting metadata

Usage help: ./manage.py cleandb -h
"""

from lxml import etree, objectify
from django.core.management.base import BaseCommand
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.utils.metadata_generator import metadata_spssodescriptor, metadata_contact


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

    def handle(self, *args, **options):
        production = options['production']
        test = options['test']
        metadata_output = options['metadata']
        attributefilter_output = options['attributefilter']
        include = options['include']
        validated = not options['unvalidated']
        if not production and not test and not include:
            self.stdout.write("Give production, test or included entityIDs as command line arguments")
        if validated:
            serviceproviders = ServiceProvider.objects.none()
            sp_loop = ServiceProvider.objects.filter(end_at=None)
            for sp in sp_loop:
                if not sp.validated:
                    sp = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
                if sp and production and sp.production:
                    serviceproviders = serviceproviders | ServiceProvider.objects.filter(pk=sp.pk)
                if sp and test and sp.test:
                    serviceproviders = serviceproviders | ServiceProvider.objects.filter(pk=sp.pk)
                if sp and include and sp.entity_id in include:
                    serviceproviders = serviceproviders | ServiceProvider.objects.filter(pk=sp.pk)
        else:
            serviceproviders = ServiceProvider.objects.none()
            if production:
                serviceproviders = serviceproviders | ServiceProvider.objects.filter(end_at=None, production=True)
            if test:
                serviceproviders = serviceproviders | ServiceProvider.objects.filter(end_at=None, test=True)
            if include:
                for entity_id in include:
                    serviceproviders = serviceproviders | ServiceProvider.objects.filter(entity_id=entity_id, end_at=None)
        # Create XML containing selected EntityDescriptors
        if serviceproviders:
            if metadata_output:
                metadata = etree.Element("EntitiesDescriptor", Name="urn:mace:funet.fi:helsinki.fi", nsmap={"xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                                                                            "ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                                                                            "mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
                for sp in serviceproviders:
                    EntityDescriptor = etree.SubElement(metadata, "EntityDescriptor", entityID=sp.entity_id)
                    metadata_spssodescriptor(EntityDescriptor, sp, validated)
                    metadata_contact(EntityDescriptor, sp, validated)
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
