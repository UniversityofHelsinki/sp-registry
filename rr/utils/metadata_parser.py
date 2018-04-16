"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.certificate import Certificate, load_certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.attribute import Attribute
from cryptography.hazmat.primitives.serialization import Encoding
from lxml import etree, objectify
from django.utils import timezone
from django.utils.translation import ugettext as _
import logging
from rr.models.nameidformat import NameIDFormat

logger = logging.getLogger(__name__)


def metadata_parser_uiinfo(sp, element):
    """
    Parses SP metadata extesions UIinfo

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "DisplayName":
            if child.values()[0] == "fi":
                sp.name_fi = child.text
            elif child.values()[0] == "en":
                sp.name_en = child.text
            elif child.values()[0] == "sv":
                sp.name_sv = child.text
        if etree.QName(child.tag).localname == "Description":
            if child.values()[0] == "fi":
                sp.description_fi = child.text
            elif child.values()[0] == "en":
                sp.description_en = child.text
            elif child.values()[0] == "sv":
                sp.description_sv = child.text
        if etree.QName(child.tag).localname == "PrivacyStatementURL":
            if child.values()[0] == "fi":
                sp.privacypolicy_fi = child.text
            elif child.values()[0] == "en":
                sp.privacypolicy_en = child.text
            elif child.values()[0] == "sv":
                sp.privacypolicy_sv = child.text


def metadata_parser_requestinitiator(sp, element):
    """
    Parses SP metadata extesions request initiator

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    sp.login_page_url = element.get("Location", "")


def metadata_parser_extensions(sp, element):
    """
    Parses SP metadata extesions

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "UIInfo":
            metadata_parser_uiinfo(sp, child)
        if etree.QName(child.tag).localname == "RequestInitiator":
            metadata_parser_requestinitiator(sp, child)


def metadata_parser_keydescriptor(sp, element, validate, errors):
    """
    Parses SP certificates

    sp: ServiceProvider object where information is linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    errors: list of errors
    """
    signing = False
    encryption = False
    key_use = element.get("use")
    if key_use == "signing":
        signing = True
    if key_use == "encryption":
        encryption = True
    if not signing and not encryption:
        signing = True
        encryption = True
    for child in element.iter(tag="{*}X509Certificate"):
        cert = load_certificate(child.text.strip())
        certificate = cert.public_bytes(Encoding.PEM).decode("utf-8").replace(
            "-----BEGIN CERTIFICATE-----\n", "").replace("-----END CERTIFICATE-----\n", "")
        if not Certificate.objects.filter(certificate=certificate, sp=sp, signing=signing, encryption=encryption):
            if not Certificate.objects.add_certificate(certificate=certificate,
                                                       sp=sp,
                                                       signing=signing,
                                                       encryption=encryption,
                                                       validate=validate):
                errors.append(sp.entity_id + " : " + _("Could not add certificate"))


def metadata_parser_nameidformat(sp, element, errors):
    """
    Parses SP nameidformat

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    errors: list of errors
    """
    try:
        nameid = NameIDFormat.objects.get(nameidformat=element.text)
        sp.nameidformat.add(nameid)
    except NameIDFormat.DoesNotExist:
        errors.append(sp.entity_id + " : " + _("Unsupported nameid-format") + " : " + str(element.text))


def metadata_parser_servicetype(sp, element, validate, errors, servicetype, disable_checks):
    """
    Parses SP endpoint bindings for a certain servicetype

    sp: ServiceProvider object where information is linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    errors: list of errors
    servicetype: parsed servicetype
    disalbe_checks: disable checks for endpoint bindingchoices, creating a new if nesessary
    """
    binding = element.get("Binding")
    location = element.get("Location")
    index = element.get("Index")
    if not disable_checks and binding not in [i[0] for i in Endpoint.BINDINGCHOICES]:
        errors.append(sp.entity_id + " : " + _("Unsupported binding, please contact IdP admins if you really need this") + " : " + binding)
    else:
        if not Endpoint.objects.filter(sp=sp, type=servicetype, binding=binding, url=location, index=index).exists():
            try:
                if validate:
                    Endpoint.objects.create(sp=sp,
                                            type=servicetype,
                                            binding=binding,
                                            url=location,
                                            index=index,
                                            validated=timezone.now())
                else:
                    Endpoint.objects.create(sp=sp,
                                            type=servicetype,
                                            binding=binding,
                                            url=location,
                                            index=index,
                                            validated=None)
            except:
                errors.append(sp.entity_id + " : " + _("Could not add") + " : " + servicetype)


def metadata_parser_attributeconsumingservice(sp, element, validate, errors):
    """
    Parses SP attribute consuming service

    sp: ServiceProvider object where information is saved or linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    errors: list of errors
    """
    for child in element:
        if etree.QName(child.tag).localname == "RequestedAttribute":
            friendlyname = child.get("FriendlyName")
            name = child.get("Name")
            if friendlyname:
                attribute = Attribute.objects.filter(name=name).first()
                if not attribute:
                    attribute = Attribute.objects.filter(friendlyname=friendlyname).first()
                if attribute:
                    if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
                        if validate:
                            SPAttribute.objects.create(sp=sp,
                                                       attribute=attribute,
                                                       reason="initial dump, please give the real reason",
                                                       validated=timezone.now())
                        else:
                            SPAttribute.objects.create(sp=sp,
                                                       attribute=attribute,
                                                       reason="initial dump, please give the real reason",
                                                       validated=None)
                else:
                    errors.append(sp.entity_id + " : " + _("Could not add attribute") + " : " + friendlyname + ", " + name)
        if etree.QName(child.tag).localname == "ServiceName":
            if child.values()[0] == "fi":
                sp.name_fi = child.text
            elif child.values()[0] == "en":
                sp.name_en = child.text
            elif child.values()[0] == "sv":
                sp.name_sv = child.text
        if etree.QName(child.tag).localname == "ServiceDescription":
            if child.values()[0] == "fi":
                sp.description_fi = child.text
            elif child.values()[0] == "en":
                sp.description_en = child.text
            elif child.values()[0] == "sv":
                sp.description_sv = child.text


def metadata_parser_ssodescriptor(sp, element, validate, errors, disable_checks):
    """
    Parses SP SSODescriptor

    sp: ServiceProvider object where information is saved or linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    errors: list of errors
    disalbe_checks: disable checks for endpoint bindingchoices, creating a new if nesessary
    """
    if element.get("AuthnRequestsSigned") == "true" or element.get("AuthnRequestsSigned") == "1":
        sp.sign_requests = True
    if element.get("WantAssertionsSigned") == "true" or element.get("WantAssertionsSigned") == "1":
        sp.sign_assertions = True
    # AuthnRequestsSigned = element.get("AuthnRequestsSigned")
    for child in element:
        if etree.QName(child.tag).localname == "Extensions":
            metadata_parser_extensions(sp, child)
        if etree.QName(child.tag).localname == "KeyDescriptor":
            metadata_parser_keydescriptor(sp, child, validate, errors)
        if etree.QName(child.tag).localname == "NameIDFormat":
            metadata_parser_nameidformat(sp, child, errors)
        for servicetype in ["ArtifactResolutionService", "SingleLogoutService", "AssertionConsumerService"]:
            if etree.QName(child.tag).localname == servicetype:
                metadata_parser_servicetype(sp, child, validate, errors, servicetype, disable_checks)
        if etree.QName(child.tag).localname == "AttributeConsumingService":
            metadata_parser_attributeconsumingservice(sp, child, validate, errors)


def metadata_parser_contact(sp, element, validate):
    """
    Parses SP contact information

    sp: ServiceProvider object where information is linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    """
    contacttype = element.get("contactType")
    if contacttype == "technical" or contacttype == "administrative" or contacttype == "support":
        firstname = ""
        lastname = ""
        email = ""
        for child in element:
            if etree.QName(child.tag).localname == "GivenName":
                firstname = child.text
            if etree.QName(child.tag).localname == "SurName":
                lastname = child.text
            if etree.QName(child.tag).localname == "EmailAddress":
                email = child.text
        if not firstname:
            firstname = " "
        if not lastname:
            lastname = " "
        if not Contact.objects.filter(sp=sp, type=contacttype, firstname=firstname, lastname=lastname, email=email).exists() and email:
            if validate:
                Contact.objects.create(sp=sp,
                                       type=contacttype,
                                       firstname=firstname,
                                       lastname=lastname,
                                       email=email,
                                       validated=timezone.now())
            else:
                Contact.objects.create(sp=sp,
                                       type=contacttype,
                                       firstname=firstname,
                                       lastname=lastname,
                                       email=email,
                                       validated=None)


def metadata_parser(entity, overwrite, verbosity, validate=False, disable_checks=False):
    """
    Parses metadata and saves information to SP-object

    entity: lxml entity for one SP
    overwrite: replace/add data for existing SP
    verbosity: verbosity level for errors
    validate: automatically validate added metadata
    disalbe_checks: disable checks for endpoint bindingchoices, creating a new if nesessary

    return sp and possible errors
    """
    errors = []
    entityID = entity.get("entityID")
    skip = False
    if entityID:
        try:
            sp = ServiceProvider.objects.get(entity_id=entityID, end_at=None)
            if not overwrite:
                skip = True
                if verbosity > 1:
                    errors.append(entityID + " : " + _("EntityID already exists, skipping"))
            else:
                if verbosity > 1:
                    errors.append(entityID + " : " + _("EntityID already exists, overwriting"))
        except ServiceProvider.DoesNotExist:
            if validate:
                sp = ServiceProvider.objects.create(entity_id=entityID, service_type="saml", validated=timezone.now(), modified=False)
            else:
                sp = ServiceProvider.objects.create(entity_id=entityID, service_type="saml", validated=None, modified=True)
            if verbosity > 2:
                errors.append(entityID + " : " + _("EntityID does not exist, creating"))
        if not skip:
            for element in entity:
                if etree.QName(element.tag).localname == "SPSSODescriptor":
                    metadata_parser_ssodescriptor(sp, element, validate, errors, disable_checks)
                if etree.QName(element.tag).localname == "ContactPerson":
                    metadata_parser_contact(sp, element, validate)
            sp.save()
            return sp, errors
    else:
        errors.append(_("Could not find entityID"))
    return None, errors
