import os
from io import StringIO
from lxml import etree

from django.core.management import call_command
from django.test import RequestFactory, TestCase

from rr.models.serviceprovider import ServiceProvider
from rr.utils.saml_metadata_parser import saml_metadata_parser

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../../testdata/metadata.xml')

class ExportMetadataTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.test_metadata = open(TESTDATA_FILENAME).read()
        parser = etree.XMLParser(ns_clean=True, remove_comments=True,
                                 remove_blank_text=True)
        entity = etree.fromstring(self.test_metadata, parser)
        self.sp, self.errors = saml_metadata_parser(entity, overwrite=False, verbosity=3,
                                                    validate=True, disable_checks=False)
        self.sp.production = True
        self.sp.save()
        self.sp2 = ServiceProvider.objects.create(entity_id='test:entity:1', service_type='saml', production=True)

    def test_exportmetadata(self):
        out = StringIO()
        call_command('exportmetadata', '-p', '-u', stdout=out)
        self.assertIn('<EntitiesDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#"',
                      out.getvalue())
        self.assertIn('<EntityDescriptor entityID="https://sp.example.org/sp">',
                      out.getvalue())
        self.assertIn('<EntityDescriptor entityID="test:entity:1">',
                      out.getvalue())
