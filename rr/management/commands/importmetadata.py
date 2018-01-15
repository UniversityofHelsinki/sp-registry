"""
Command line script for importing metadata.xml

Usage: ./manage.py importmetadata <metadata-file-name>
"""

from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.attribute import Attribute
from rr.models.endpoint import Endpoint
from django.contrib.auth.models import User
from lxml import etree, objectify
from django.utils import timezone
from django.core.management.base import BaseCommand


def metadata_parser(filename):
    parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
    tree = etree.parse(filename, parser)
    root = tree.getroot()
    user = User.objects.filter(pk=1).first()
    for a in root:
        entityID = a.get("entityID")
        if entityID:
            try:
                sp = ServiceProvider.objects.get(entity_id=entityID, end_at=None)
            except ServiceProvider.DoesNotExist:
                sp = ServiceProvider.objects.create(entity_id=entityID, name_fi=entityID, validated=True, modified=False)
            for b in a:
                if etree.QName(b.tag).localname == "SPSSODescriptor":
                    AuthnRequestsSigned = b.get("AuthnRequestsSigned")
                    for c in b:
                        if etree.QName(c.tag).localname == "Extensions":
                            for d in c:
                                if etree.QName(d.tag).localname == "UIInfo":
                                    for e in d:
                                        if etree.QName(e.tag).localname == "DisplayName":
                                            if e.values()[0] == "fi":
                                                sp.name_fi = e.text
                                            elif e.values()[0] == "en":
                                                sp.name_en = e.text
                                            elif e.values()[0] == "sv":
                                                sp.name_sv = e.text
                                        if etree.QName(e.tag).localname == "Description":
                                            if e.values()[0] == "fi":
                                                sp.description_fi = e.text
                                            elif e.values()[0] == "en":
                                                sp.description_en = e.text
                                            elif e.values()[0] == "sv":
                                                sp.description_sv = e.text
                                        if etree.QName(e.tag).localname == "PrivacyStatementURL":
                                            if e.values()[0] == "fi":
                                                sp.privacypolicy_fi = e.text
                                            elif e.values()[0] == "en":
                                                sp.privacypolicy_en = e.text
                                            elif e.values()[0] == "sv":
                                                sp.privacypolicy_sv = e.text
                                if etree.QName(d.tag).localname == "RequestInitiator":
                                    RequestInitiator = c.get("Location")
                        if etree.QName(c.tag).localname == "KeyDescriptor":
                            signing = False
                            encryption = False
                            key_use = c.get("use")
                            if key_use == "signing":
                                signing = True
                            if key_use == "encryption":
                                encryption = True
                            for element in c.iter(tag="{*}X509Certificate"):
                                certificate = element.text
                                if certificate.endswith("\n"):
                                    certificate = certificate + "-----END CERTIFICATE-----\n"
                                else:
                                    certificate = certificate + "\n-----END CERTIFICATE-----\n"
                                certificate = "-----BEGIN CERTIFICATE-----\n" + certificate
                                if not Certificate.objects.filter(certificate=certificate, sp=sp, signing=signing, encryption=encryption):
                                    if not Certificate.objects.add_certificate(certificate=certificate,
                                                                               sp=sp,
                                                                               signing=signing,
                                                                               encryption=encryption):
                                        print("Could not load certificate for " + entityID)
                        if etree.QName(c.tag).localname == "NameIDFormat":
                            if c.text is "urn:oasis:names:tc:SAML:2.0:nameid-format:transient":
                                sp.name_format_transient = True
                            elif c.text is "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent":
                                sp.name_format_persistent = True
                            else:
                                print("Unsupported nameid-format " + entityID)
                        for servicetype in ["ArtifactResolutionService", "SingleLogoutService", "AssertionConsumerService"]:
                            if etree.QName(c.tag).localname == servicetype:
                                binding = c.get("Binding")
                                location = c.get("Location")
                                index = c.get("Index")
                                if not Endpoint.objects.filter(sp=sp, type=servicetype, binding=binding, url=location, index=index).exists():
                                    try:
                                        Endpoint.objects.create(sp=sp,
                                                                type=servicetype,
                                                                binding=binding,
                                                                url=location,
                                                                index=index,
                                                                validated=timezone.now())
                                    except:
                                        print("Could not add " + servicetype + " for " + entityID)
                        if etree.QName(c.tag).localname == "AttributeConsumingService":
                            for d in c:
                                if etree.QName(d.tag).localname == "RequestedAttribute":
                                    friendlyname = d.get("FriendlyName")
                                    name = d.get("Name")
                                    if friendlyname:
                                        try:
                                            attribute = Attribute.objects.get(friendlyname=friendlyname)
                                            if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
                                                SPAttribute.objects.create(sp=sp,
                                                                           attribute=attribute,
                                                                           reason="initial dump, please give the real reason",
                                                                           validated=timezone.now())
                                        except Attribute.DoesNotExist:
                                            print("Could not add attribute " + friendlyname + " for " + entityID)
                                if etree.QName(d.tag).localname == "ServiceName":
                                    if d.values()[0] == "fi":
                                        sp.name_fi = d.text
                                    elif d.values()[0] == "en":
                                        sp.name_en = d.text
                                    elif d.values()[0] == "sv":
                                        sp.name_sv = d.text
                                if etree.QName(d.tag).localname == "ServiceDescription":
                                    if d.values()[0] == "fi":
                                        sp.description_fi = d.text
                                    elif d.values()[0] == "en":
                                        sp.description_en = d.text
                                    elif d.values()[0] == "sv":
                                        sp.description_sv = d.text
                if etree.QName(b.tag).localname == "ContactPerson":
                    contacttype = b.get("contactType")
                    if contacttype == "technical" or contacttype == "administrative" or contacttype == "support":
                        firstname = ""
                        lastname = ""
                        email = ""
                        for c in b:
                            if etree.QName(c.tag).localname == "GivenName":
                                firstname = c.text
                            if etree.QName(c.tag).localname == "SurName":
                                lastname = c.text
                            if etree.QName(c.tag).localname == "EmailAddress":
                                email = c.text
                        if not Contact.objects.filter(sp=sp, type=contacttype, firstname=firstname, lastname=lastname, email=email).exists() and email:
                            Contact.objects.create(sp=sp,
                                                   type=contacttype,
                                                   firstname=firstname,
                                                   lastname=lastname,
                                                   email=email,
                                                   validated=timezone.now())
            sp.save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        for file in options['files']:
            metadata_parser(file)
