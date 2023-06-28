"""
Command line script for exporting metadata

Usage help: ./manage.py exportattributefilter -h
"""

from argparse import FileType

from django.core.management.base import BaseCommand
from lxml import etree

from rr.models.serviceprovider import ServiceProvider, SPAttribute


class Command(BaseCommand):
    help = "Exports validated metadata"

    def add_arguments(self, parser):
        parser.add_argument("-p", action="store_true", dest="production", help="Include production service providers")
        parser.add_argument("-t", action="store_true", dest="test", help="Include test service providers")
        parser.add_argument("-o", type=FileType("w"), dest="output", help="Output file name")
        parser.add_argument(
            "-i", type=str, nargs="+", action="store", dest="include", help="List of included entityIDs"
        )
        parser.add_argument("-u", action="store_true", dest="unvalidated", help="Use unvalidated data")

    def handle(self, *args, **options):
        production = options["production"]
        test = options["test"]
        output_file = options["output"] if options["output"] else self.stdout
        include = options["include"]
        validated = not options["unvalidated"]
        if not production and not test and not include:
            self.stderr.write(
                "Give production, test or included entityIDs as command line " 'arguments, use "-h" for help.'
            )
            exit(1)
        # Create XML containing selected EntityDescriptors
        attributefilter = etree.Element(
            "AttributeFilterPolicyGroup", id="urn:mace:funet.fi:haka", nsmap={"xmlns": "urn:mace:shibboleth:2.0:afp"}
        )
        attributefilter.attrib["{urn:mace:shibboleth:2.0:afp}basic"] = "urn:mace:shibboleth:2.0:afp:mf:basic"
        attributefilter.attrib["{urn:mace:shibboleth:2.0:afp}saml"] = "urn:mace:shibboleth:2.0:afp:mf:saml"
        attributefilter.attrib["{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"] = (
            "urn:mace:shibboleth:2.0:afp classpath:/schema/shibboleth-2.0-afp.xsd "
            "urn:mace:shibboleth:2.0:afp:mf:basic "
            "classpath:/schema/shibboleth-2.0-afp-mf-basic.xsd "
            "urn:mace:shibboleth:2.0:afp:mf:saml "
            "classpath:/schema/shibboleth-2.0-afp-mf-saml.xsd"
        )
        serviceproviders = ServiceProvider.objects.filter(end_at=None)
        for sp in serviceproviders:
            if (production and sp.production) or (test and sp.test) or (include and sp.entity_id in include):
                if validated:
                    attributes = SPAttribute.objects.filter(sp=sp, end_at=None).exclude(validated=None)
                else:
                    attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
                if attributes:
                    attribute_filter_policy = etree.SubElement(
                        attributefilter, "AttributeFilterPolicy", id="hy-default-" + sp.entity_id
                    )
                    policy_requirement_rule = etree.SubElement(
                        attribute_filter_policy, "PolicyRequirementRule", value=sp.entity_id
                    )
                    policy_requirement_rule.attrib[
                        "{http://www.w3.org/2001/XMLSchema-instance}type"
                    ] = "basic:AttributeRequesterString"
                    for attribute in attributes:
                        attribute_rule = etree.SubElement(
                            attribute_filter_policy, "AttributeRule", attributeID=attribute.attribute.attributeid
                        )
                        permit_value_rule = etree.SubElement(attribute_rule, "PermitValueRule")
                        permit_value_rule.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] = "basic:ANY"

            output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            # Hack for correcting namespace definition by removing prefix.
            output_file.write(
                etree.tostring(attributefilter, pretty_print=True, encoding="unicode").replace("xmlns:xmlns", "xmlns")
            )
