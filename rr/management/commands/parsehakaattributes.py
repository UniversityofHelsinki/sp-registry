"""
Parse a Haka metadata file and print out attribute-filter for it.
Short term manual hack for IdP 2 as Haka stopped releasing attribute-filter file.

Usage: ./manage.py parsehakaattributes <metadata-file-name>
Saves output to "attribute-filter-haka.xml_YYYYMMDD"
"""

from rr.models.attribute import Attribute
from lxml import etree, objectify
from django.core.management.base import BaseCommand
from datetime import date


def haka_attribute_parser(filename):
    """
    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    AttributeFilterPolicyGroup = etree.Element("AttributeFilterPolicyGroup", id="urn:mace:funet.fi:haka", nsmap={"xmlns": 'urn:mace:shibboleth:2.0:afp'})
    AttributeFilterPolicyGroup.attrib['{urn:mace:shibboleth:2.0:afp}basic'] = "urn:mace:shibboleth:2.0:afp:mf:basic"
    AttributeFilterPolicyGroup.attrib['{urn:mace:shibboleth:2.0:afp}saml'] = "urn:mace:shibboleth:2.0:afp:mf:saml"
    AttributeFilterPolicyGroup.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = "urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd urn:mace:shibboleth:2.0:afp:mf:basic classpath:/schema/shibboleth-2.0-afp-mf-basic.xsd urn:mace:shibboleth:2.0:afp:mf:saml classpath:/schema/shibboleth-2.0-afp-mf-saml.xsd"
    for a in root:
        entityID = a.get("entityID")
        if entityID:
            for b in a:
                if etree.QName(b.tag).localname == "SPSSODescriptor":
                    attributes = []
                    for c in b:
                        if etree.QName(c.tag).localname == "AttributeConsumingService":
                            for d in c:
                                if etree.QName(d.tag).localname == "RequestedAttribute":
                                    friendlyname = d.get("FriendlyName")
                                    name = d.get("Name")
                                    if friendlyname:
                                        attribute = Attribute.objects.filter(name=name).first()
                                        if not attribute:
                                            attribute = Attribute.objects.filter(friendlyname=friendlyname).first()
                                        if attribute:
                                            attributes.append(attribute)
                                        else:
                                            print("Could not add attribute " + friendlyname + ", " + name + " for " + entityID)
                    if attributes:
                        AttributeFilterPolicy = etree.SubElement(AttributeFilterPolicyGroup, "AttributeFilterPolicy", id="haka-default-" + entityID)
                        PolicyRequirementRule = etree.SubElement(AttributeFilterPolicy, "PolicyRequirementRule", value=entityID)
                        PolicyRequirementRule.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "basic:AttributeRequesterString"
                        for attribute in attributes:
                            AttributeRule = etree.SubElement(AttributeFilterPolicy, "AttributeRule", attributeID=attribute.attributeid)
                            PermitValueRule = etree.SubElement(AttributeRule, "PermitValueRule")
                            PermitValueRule.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "basic:ANY"
    return(etree.tostring(AttributeFilterPolicyGroup, pretty_print=True, encoding='UTF-8'))


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', type=str, action='store', dest='input', help='Metadata input file name')
        parser.add_argument('-o', type=str, action='store', dest='output', help='Attribute-filter output file name')

    def handle(self, *args, **options):
        metadata_input = options['input']
        attribute_output = options['output']
        if metadata_input and attribute_output:
            data = haka_attribute_parser(metadata_input)
            with open(attribute_output, 'wb') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                # Hack for correcting namespace definition by removing prefix.
                f.write(data.replace(b'xmlns:xmlns', b'xmlns'))
        else:
            self.stdout.write("Please give both input and output files")
