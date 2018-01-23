"""
Parse a Haka metadata file and print out attribute-filter for it.
Short term manual hack for IdP 2 as Haka stopped releasing attribute-filter file.

Usage: ./manage.py parsehakaattributes <metadata-file-name>
Saves output to "attribute-filter-haka.xml_YYYYMMDD"
"""

from lxml import etree, objectify
from django.core.management.base import BaseCommand
from datetime import date
from rr.models.serviceprovider import ServiceProvider
from rr.views.metadata import metadata_spssodescriptor, metadata_contact


class Command(BaseCommand):
    help = 'Exports validated metadata'

    def add_arguments(self, parser):
        parser.add_argument('-p', action='store_true', dest='production', help='Include production service providers')
        parser.add_argument('-t', action='store_true', dest='test', help='Include test service providers')
        parser.add_argument('-m', type=str, action='store', dest='metadata', help='Metadata output file name')
        parser.add_argument('-i', type=str,  nargs='+', action='store', dest='include', help='List of included entityIDs')

    def handle(self, *args, **options):
        production = options['production']
        test = options['test']
        metadata_output = options['metadata']
        include = options['include']
        if not production and not test and not include:
            self.stdout.write("Specify production, test or included entityIDs")
        serviceproviders = ServiceProvider.objects.none()
        if production:
            serviceproviders = serviceproviders | ServiceProvider.objects.filter(end_at=None, production=True).exclude(validated=None)
        if test:
            serviceproviders = serviceproviders | ServiceProvider.objects.filter(end_at=None, test=True).exclude(validated=None)
        if include:
            for entity_id in include:
                serviceproviders = serviceproviders | ServiceProvider.objects.filter(entity_id=entity_id, end_at=None).exclude(validated=None)
        if serviceproviders:
            NSMAL = {"xmlns": 'urn:mace:shibboleth:2.0:afp',
                     }
            metadata = etree.Element("EntitiesDescriptor", name="urn:mace:funet.fi:helsinki.fi")
            metadata.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = "urn:oasis:names:tc:SAML:2.0:metadata saml-schema-metadata-2.0.xsd urn:mace:shibboleth:metadata:1.0 shibboleth-metadata-1.0.xsd http://www.w3.org/2000/09/xmldsig# xmldsig-core-schema.xsd"
            for sp in serviceproviders:
                EntityDescriptor = etree.SubElement(metadata, "EntityDescriptor", entityID=sp.entity_id)
                metadata_spssodescriptor(EntityDescriptor, sp)
                metadata_contact(EntityDescriptor, sp)
            if metadata_output:
                with open(metadata_output, 'wb') as f:
                    f.write(etree.tostring(metadata, pretty_print=True))
            else:
                self.stdout.write(etree.tostring(metadata, pretty_print=True).decode('utf-8'))
