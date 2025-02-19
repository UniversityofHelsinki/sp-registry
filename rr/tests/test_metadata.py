import os

from django.contrib.auth.models import User
from django.test import TestCase
from lxml import etree

from rr.models.attribute import Attribute
from rr.models.nameidformat import NameIDFormat
from rr.models.organization import Organization
from rr.utils.saml_metadata_generator import (
    saml_metadata_generator,
    saml_metadata_generator_list,
)
from rr.utils.saml_metadata_parser import saml_metadata_parser

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), "../testdata/metadata.xml")
TESTDATA_MINIMAL_FILENAME = os.path.join(os.path.dirname(__file__), "../testdata/metadata_minimal.xml")
TESTDATA_MINIMAL_ORGANIZATION_FILENAME = os.path.join(
    os.path.dirname(__file__), "../testdata/metadata_minimal_organization.xml"
)


class MetadataParserGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.attr_cn = Attribute.objects.create(
            friendlyname="cn",
            name="urn:oid:2.5.4.3",
            attributeid="id-urn:mace:dir:attribute-def:cn",
            nameformat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            public_saml=True,
            public_ldap=True,
        )
        self.attr_eppn = Attribute.objects.create(
            friendlyname="eduPersonPrincipalName",
            name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6",
            attributeid="id-urn:mace:dir:attribute-def:eduPersonPrincipalName",
            nameformat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            public_saml=True,
            public_ldap=False,
        )
        self.nameidformat = NameIDFormat.objects.create(
            nameidformat="urn:oasis:names:tc:SAML:2.0:nameid-format:transient", public=True
        )
        self.test_metadata = open(TESTDATA_FILENAME).read()
        parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
        entity = etree.fromstring(self.test_metadata, parser)
        self.sp, self.errors = saml_metadata_parser(
            entity, overwrite=False, verbosity=2, validate=True, disable_checks=False
        )
        self.maxDiff = None

    def test_metadata_parser(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.sp.force_nameidformat, True)
        self.assertEqual(self.sp.force_sha1, True)
        self.assertEqual(self.sp.force_mfa, True)
        self.assertEqual(self.sp.encrypt_assertions, False)
        self.assertEqual(self.sp.sign_responses, False)
        self.assertEqual(self.sp.sign_requests, True)
        self.assertEqual(self.sp.sign_assertions, True)
        self.assertEqual(self.sp.saml_subject_identifier, "pairwise-id")
        self.assertEqual(self.sp.nameidformat.all().count(), 1)
        self.assertEqual(self.sp.discovery_service_url, "https://sp.example.org/Shibboleth.sso/DS")
        self.assertEqual(self.sp.login_page_url, "https://sp.example.org/Shibboleth.sso/Login")
        self.assertEqual(self.sp.name_fi, "Testiohjelma")
        self.assertEqual(self.sp.name_en, "Test application")
        self.assertEqual(self.sp.name_sv, "Testapplikation")
        self.assertEqual(self.sp.description_fi, "Testimetadata resurssirekisteriin")
        self.assertEqual(self.sp.description_en, "Testing metadata for resource registry")
        self.assertEqual(self.sp.description_sv, "Testa metadata för resursregistret")
        self.assertEqual(self.sp.privacypolicy_fi, "https://sp.example.org/privacy/policy_fi.pdf")
        self.assertEqual(self.sp.privacypolicy_en, "https://sp.example.org/privacy/policy_en.pdf")
        self.assertEqual(self.sp.privacypolicy_sv, "https://sp.example.org/privacy/policy_sv.pdf")

    def test_metadata_generation(self):
        metadata_tree = saml_metadata_generator(sp=self.sp)
        metadata = etree.tostring(metadata_tree, pretty_print=True, encoding="UTF-8").replace(b"xmlns:xmlns", b"xmlns")
        self.assertEqual(metadata.decode("utf-8"), self.test_metadata)


class MetadataMinimalParserGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.superuser = User.objects.create(username="superuser", is_superuser=True)
        self.attr_cn = Attribute.objects.create(
            friendlyname="cn",
            name="urn:oid:2.5.4.3",
            attributeid="id-urn:mace:dir:attribute-def:cn",
            nameformat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            public_saml=True,
            public_ldap=True,
        )
        self.attr_eppn = Attribute.objects.create(
            friendlyname="eduPersonPrincipalName",
            name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6",
            attributeid="id-urn:mace:dir:attribute-def:eduPersonPrincipalName",
            nameformat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            public_saml=True,
            public_ldap=False,
        )
        self.nameidformat = NameIDFormat.objects.create(
            nameidformat="urn:oasis:names:tc:SAML:2.0:nameid-format:transient", public=True
        )
        self.test_metadata = open(TESTDATA_MINIMAL_FILENAME).read()
        parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
        entity = etree.fromstring(self.test_metadata, parser)
        self.sp, self.errors = saml_metadata_parser(
            entity, overwrite=False, verbosity=2, validate=True, disable_checks=False
        )
        self.sp.production = True
        self.sp.save()

    def test_metadata_parser(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.sp.force_nameidformat, False)
        self.assertEqual(self.sp.force_sha1, False)
        self.assertEqual(self.sp.force_mfa, False)
        self.assertEqual(self.sp.encrypt_assertions, True)
        self.assertEqual(self.sp.sign_responses, True)
        self.assertEqual(self.sp.sign_requests, False)
        self.assertEqual(self.sp.sign_assertions, False)
        self.assertEqual(self.sp.nameidformat.all().count(), 0)
        self.assertEqual(self.sp.discovery_service_url, "")
        self.assertEqual(self.sp.login_page_url, "")
        self.assertEqual(self.sp.name_fi, "")
        self.assertEqual(self.sp.name_en, "")
        self.assertEqual(self.sp.name_sv, "")
        self.assertEqual(self.sp.description_fi, "")
        self.assertEqual(self.sp.description_en, "")
        self.assertEqual(self.sp.description_sv, "")
        self.assertEqual(self.sp.privacypolicy_fi, "")
        self.assertEqual(self.sp.privacypolicy_en, "")
        self.assertEqual(self.sp.privacypolicy_sv, "")

    def test_metadata_generation(self):
        metadata_tree = saml_metadata_generator(sp=self.sp)
        metadata = etree.tostring(metadata_tree, pretty_print=True, encoding="UTF-8").replace(b"xmlns:xmlns", b"xmlns")
        self.assertEqual(metadata.decode("utf-8"), self.test_metadata)

    def test_metadata_generation_as_list(self):
        metadata_list = saml_metadata_generator_list(production=True)
        metadata = etree.tostring(metadata_list[0], pretty_print=True, encoding="UTF-8").replace(
            b"xmlns:xmlns", b"xmlns"
        )
        self.assertEqual(metadata.decode("utf-8"), self.test_metadata)

    def test_metadata_organization_generation(self):
        organization = Organization.objects.create(
            name_fi="Testiorganisaatio",
            name_en="Test Organization",
            description_en="Descriptiontest",
            url_sv="https://example.org/sv",
            url_en="https://example.org/",
            privacypolicy_fi="https://www.example.org/tietosuoja",
            privacypolicy_en="https://www.example.org/data-protection",
            privacypolicy_sv="https://www.example.org/dataskydd",
        )
        self.sp.organization = organization
        self.sp.privacypolicy_org = True
        self.sp.save()
        metadata_tree = saml_metadata_generator(sp=self.sp)
        metadata = etree.tostring(metadata_tree, pretty_print=True, encoding="UTF-8").replace(b"xmlns:xmlns", b"xmlns")
        self.assertEqual(metadata.decode("utf-8"), open(TESTDATA_MINIMAL_ORGANIZATION_FILENAME).read())
