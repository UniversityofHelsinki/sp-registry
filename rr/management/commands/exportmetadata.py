"""
Command line script for exporting metadata

Usage: ./manage.py exportmetadata -o <output-file-name> -p -t -i entityId [entityId]
-p                include production data
-t                include test data
-- unvalidated    use unvalidated metadata
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
        parser.add_argument('-u', action='store_true', dest='unvalidated', help='Use unvalidated data')

    def handle(self, *args, **options):
        production = options['production']
        test = options['test']
        metadata_output = options['metadata']
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
            metadata = etree.Element("EntitiesDescriptor", name="urn:mace:funet.fi:helsinki.fi")
            metadata.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = "urn:oasis:names:tc:SAML:2.0:metadata saml-schema-metadata-2.0.xsd urn:mace:shibboleth:metadata:1.0 shibboleth-metadata-1.0.xsd http://www.w3.org/2000/09/xmldsig# xmldsig-core-schema.xsd"
            for sp in serviceproviders:
                EntityDescriptor = etree.SubElement(metadata, "EntityDescriptor", entityID=sp.entity_id)
                metadata_spssodescriptor(EntityDescriptor, sp, validated)
                metadata_contact(EntityDescriptor, sp, validated)
            if metadata_output:
                with open(metadata_output, 'wb') as f:
                    f.write(etree.tostring(metadata, pretty_print=True))
            else:
                self.stdout.write(etree.tostring(metadata, pretty_print=True).decode('utf-8'))