"""
Parse a Haka metadata file and print out attribute-filter for it.
Short term manual hack for IdP 2 as Haka stopped releasing attribute-filter file.

Usage help: ./manage.py cleandb -h
"""
from django.core.management.base import BaseCommand
from lxml import etree

from rr.models.attribute import Attribute


def haka_attribute_parser(filename):
    """
    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    parser = etree.XMLParser(
        ns_clean=True, remove_comments=True, remove_blank_text=True, resolve_entities=False, no_network=True
    )
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    attribute_filter_policy_group = etree.Element(
        "AttributeFilterPolicyGroup", id="urn:mace:funet.fi:haka", nsmap={"xmlns": "urn:mace:shibboleth:2.0:afp"}
    )
    attribute_filter_policy_group.attrib["{urn:mace:shibboleth:2.0:afp}basic"] = "urn:mace:shibboleth:2.0:afp:mf:basic"
    attribute_filter_policy_group.attrib["{urn:mace:shibboleth:2.0:afp}saml"] = "urn:mace:shibboleth:2.0:afp:mf:saml"
    attribute_filter_policy_group.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"] = (
        "urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd "
        "urn:mace:shibboleth:2.0:afp:mf:basic "
        "classpath:/schema/shibboleth-2.0-afp-mf-basic.xsd "
        "urn:mace:shibboleth:2.0:afp:mf:saml "
        "classpath:/schema/shibboleth-2.0-afp-mf-saml.xsd"
    )
    for a in root:
        entity_id = a.get("entityID")
        if entity_id:
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
                                            print(
                                                "Could not add attribute "
                                                + friendlyname
                                                + ", "
                                                + name
                                                + " for "
                                                + entity_id
                                            )
                    if attributes:
                        attribute_filter_policy = etree.SubElement(
                            attribute_filter_policy_group, "AttributeFilterPolicy", id="haka-default-" + entity_id
                        )
                        policy_requirement_rule = etree.SubElement(
                            attribute_filter_policy, "PolicyRequirementRule", value=entity_id
                        )
                        policy_requirement_rule.attrib[
                            "{http://www.w3.org/2001/XMLSchema-instance}type"
                        ] = "basic:AttributeRequesterString"
                        for attribute in attributes:
                            attribute_rule = etree.SubElement(
                                attribute_filter_policy, "AttributeRule", attributeID=attribute.attributeid
                            )
                            permit_value_rule = etree.SubElement(attribute_rule, "PermitValueRule")
                            permit_value_rule.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] = "basic:ANY"
    return etree.tostring(attribute_filter_policy_group, pretty_print=True, encoding="UTF-8")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-i", type=str, action="store", dest="input", help="Metadata input file name")
        parser.add_argument("-o", type=str, action="store", dest="output", help="Attribute-filter output file name")

    def handle(self, *args, **options):
        metadata_input = options["input"]
        attribute_output = options["output"]
        if metadata_input and attribute_output:
            data = haka_attribute_parser(metadata_input)
            with open(attribute_output, "wb") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode("utf-8"))
                # Hack for correcting namespace definition by removing prefix.
                f.write(data.replace(b"xmlns:xmlns", b"xmlns"))
        else:
            self.stdout.write("Please give both input and output files")
