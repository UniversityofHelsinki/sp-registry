"""
Functions for genereating metadata of service providers
"""
import logging

from cryptography.hazmat.primitives.serialization import Encoding
from lxml import etree

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.models.attribute import Attribute
from rr.models.certificate import Certificate, load_certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.nameidformat import NameIDFormat
from rr.models.serviceprovider import ServiceProvider, SPAttribute

logger = logging.getLogger(__name__)


def metadata_parser_uiinfo(sp, element):
    """
    Parses SP metadata extensions UIinfo

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "DisplayName":
            if child.values()[0] == "fi" and child.text:
                sp.name_fi = child.text
            elif child.values()[0] == "en" and child.text:
                sp.name_en = child.text
            elif child.values()[0] == "sv" and child.text:
                sp.name_sv = child.text
        if etree.QName(child.tag).localname == "Description":
            if child.values()[0] == "fi" and child.text:
                sp.description_fi = child.text
            elif child.values()[0] == "en" and child.text:
                sp.description_en = child.text
            elif child.values()[0] == "sv" and child.text:
                sp.description_sv = child.text
        if etree.QName(child.tag).localname == "PrivacyStatementURL":
            if child.values()[0] == "fi" and child.text:
                sp.privacypolicy_fi = child.text
            elif child.values()[0] == "en" and child.text:
                sp.privacypolicy_en = child.text
            elif child.values()[0] == "sv" and child.text:
                sp.privacypolicy_sv = child.text


def metadata_parser_requestinitiator(sp, element):
    """
    Parses SP metadata extesions request initiator

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    sp.login_page_url = element.get("Location", "")


def metadata_parser_discoveryresponse(sp, element):
    """
    Parses SP metadata extesions discovery response

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    sp.discovery_service_url = element.get("Location", "")


def metadata_parser_spsso_extensions(sp, element):
    """
    Parses SP metadata spsso extesions

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "UIInfo":
            metadata_parser_uiinfo(sp, child)
        if etree.QName(child.tag).localname == "RequestInitiator":
            metadata_parser_requestinitiator(sp, child)
        if etree.QName(child.tag).localname == "DiscoveryResponse":
            metadata_parser_discoveryresponse(sp, child)


def metadata_parser_entityattributes(sp, element):
    """
    Parses SP metadata extesions entityattributes

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "Attribute" and  etree.QName(child[0].tag).localname == "AttributeValue":
            if (child.get("Name") == "http://shibboleth.net/ns/profiles/defaultAuthenticationMethods" and
                    child[0].text == settings.MFA_AUTHENTICATION_CONTEXT):
                sp.force_mfa = True
            if child.get("Name") == "http://shibboleth.net/ns/profiles/nameIDFormatPrecedence":
                sp.force_nameidformat = True
            if (child.get("Name") == "http://shibboleth.net/ns/profiles/saml2/sso/browser/signResponses" and
                    child[0].text == "false"):
                sp.sign_responses = False
            if (child.get("Name") == "http://shibboleth.net/ns/profiles/saml2/sso/browser/encryptAssertions" and
                    child[0].text == "false"):
                sp.encrypt_assertions = False
            if (child.get("Name") == "http://shibboleth.net/ns/profiles/securityConfiguration" and
                    child[0].text == "shibboleth.SecurityConfiguration.SHA1"):
                sp.force_sha1 = True


def metadata_parser_extensions(sp, element):
    """
    Parses SP metadata extesions

    sp: ServiceProvider object where information is saved
    element: lxml element which is parsed
    """
    for child in element:
        if etree.QName(child.tag).localname == "EntityAttributes":
            metadata_parser_entityattributes(sp, child)


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
        if (not Certificate.objects.filter(certificate=certificate,
                                           sp=sp,
                                           signing=signing,
                                           encryption=encryption) and not
                Certificate.objects.add_certificate(certificate=certificate,
                                                    sp=sp,
                                                    signing=signing,
                                                    encryption=encryption,
                                                    validate=validate)):
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
        errors.append(
            sp.entity_id + " : " + _("Unsupported nameid-format") + " : " + str(element.text))


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
    response_location = element.get("ResponseLocation", '')
    default = element.get("isDefault")
    index = _parse_index(element)
    if default and default.lower() == "true" and index:
        is_default = True
    else:
        is_default = False
    if not disable_checks and binding not in [i[0] for i in Endpoint.BINDINGCHOICES]:
        errors.append(
            sp.entity_id + " : " +
            _("Unsupported binding, please contact IdP admins if you really need this") +
            " : " + binding)
    else:
        if ((Endpoint.objects.filter(
                sp=sp, type=servicetype, binding=binding, location=location, end_at=None).exists()) or
                (index and Endpoint.objects.filter(
                    sp=sp, type=servicetype, binding=binding, index=index, end_at=None).exists()) or
                (is_default and Endpoint.objects.filter(
                    sp=sp, type=servicetype, binding=binding, is_default=True, end_at=None).exists())):
            return
        try:
            if validate:
                Endpoint.objects.create(sp=sp,
                                        type=servicetype,
                                        binding=binding,
                                        location=location,
                                        response_location=response_location,
                                        index=index,
                                        is_default=is_default,
                                        validated=timezone.now())
            else:
                Endpoint.objects.create(sp=sp,
                                        type=servicetype,
                                        binding=binding,
                                        location=location,
                                        response_location=response_location,
                                        index=index,
                                        is_default=is_default,
                                        validated=None)
        except ValidationError:
            errors.append(sp.entity_id + " : " + _("Could not add") + " : " + servicetype)


def _parse_index(element):
    index = element.get("index")
    try:
        return int(index)
    except ValueError:
        return None
    except TypeError:
        return None


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
            errors = _parse_attribute(sp, child, validate, errors)
        if etree.QName(child.tag).localname == "ServiceName":
            if child.values()[0] == "fi" and child.text:
                sp.name_fi = child.text
            elif child.values()[0] == "en" and child.text:
                sp.name_en = child.text
            elif child.values()[0] == "sv" and child.text:
                sp.name_sv = child.text
        if etree.QName(child.tag).localname == "ServiceDescription":
            if child.values()[0] == "fi" and child.text:
                sp.description_fi = child.text
            elif child.values()[0] == "en" and child.text:
                sp.description_en = child.text
            elif child.values()[0] == "sv" and child.text:
                sp.description_sv = child.text


def _parse_attribute(sp, element, validate, errors):
    friendly_name = element.get("FriendlyName")
    name = element.get("Name")
    if friendly_name:
        attribute = Attribute.objects.filter(name=name).first()
        if not attribute:
            attribute = Attribute.objects.filter(friendlyname=friendly_name).first()
        if attribute:
            if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
                if validate:
                    SPAttribute.objects.create(
                        sp=sp,
                        attribute=attribute,
                        reason="initial dump, please give the real reason",
                        validated=timezone.now())
                else:
                    SPAttribute.objects.create(
                        sp=sp,
                        attribute=attribute,
                        reason="initial dump, please give the real reason",
                        validated=None)
        else:
            errors.append(
                sp.entity_id + " : " +
                _("Could not add attribute") + " : " + friendly_name + ", " + name)


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
    for child in element:
        if etree.QName(child.tag).localname == "Extensions":
            metadata_parser_spsso_extensions(sp, child)
        if etree.QName(child.tag).localname == "KeyDescriptor":
            metadata_parser_keydescriptor(sp, child, validate, errors)
        if etree.QName(child.tag).localname == "NameIDFormat":
            metadata_parser_nameidformat(sp, child, errors)
        for servicetype in ["ArtifactResolutionService", "SingleLogoutService",
                            "AssertionConsumerService"]:
            if etree.QName(child.tag).localname == servicetype:
                metadata_parser_servicetype(sp, child, validate, errors, servicetype,
                                            disable_checks)
        if etree.QName(child.tag).localname == "AttributeConsumingService":
            metadata_parser_attributeconsumingservice(sp, child, validate, errors)


def metadata_parser_contact(sp, element, validate):
    """
    Parses SP contact information

    sp: ServiceProvider object where information is linked
    element: lxml element which is parsed
    validate: automatically validate added metadata
    """
    contact_type = element.get("contactType")
    if contact_type == "technical" or contact_type == "administrative" or contact_type == "support":
        first_name, last_name, email = _parse_contact_info(element)
        if not Contact.objects.filter(sp=sp, type=contact_type, firstname=first_name,
                                      lastname=last_name, email=email).exists() and email:
            if validate:
                Contact.objects.create(sp=sp,
                                       type=contact_type,
                                       firstname=first_name,
                                       lastname=last_name,
                                       email=email,
                                       validated=timezone.now())
            else:
                Contact.objects.create(sp=sp,
                                       type=contact_type,
                                       firstname=first_name,
                                       lastname=last_name,
                                       email=email,
                                       validated=None)


def _parse_contact_info(element):
    first_name = ""
    last_name = ""
    email = ""
    for child in element:
        if etree.QName(child.tag).localname == "GivenName":
            first_name = child.text
        if etree.QName(child.tag).localname == "SurName":
            last_name = child.text
        if etree.QName(child.tag).localname == "EmailAddress":
            email = child.text
    if not first_name:
        first_name = " "
    if not last_name:
        last_name = " "
    return first_name, last_name, email


def metadata_parse_element(element, sp, validate, errors, disable_checks):
    if etree.QName(element.tag).localname == "SPSSODescriptor":
        metadata_parser_ssodescriptor(sp, element, validate, errors, disable_checks)
    if etree.QName(element.tag).localname == "ContactPerson":
        metadata_parser_contact(sp, element, validate)
    if etree.QName(element.tag).localname == "Extensions":
        metadata_parser_extensions(sp, element)


def saml_metadata_parser(entity, overwrite, verbosity, validate=False, disable_checks=False):
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
    entity_id = entity.get("entityID")
    if entity_id:
        sp, errors = _get_sp(entity_id, errors, validate, overwrite, verbosity)
        if sp:
            for element in entity:
                metadata_parse_element(element, sp, validate, errors, disable_checks)
            sp.save()
            return sp, errors
    else:
        errors.append(_("Could not find entityID"))
    return None, errors


def _get_sp(entity_id, errors, validate, overwrite, verbosity):
    try:
        sp = ServiceProvider.objects.get(entity_id=entity_id, end_at=None)
        if not overwrite:
            sp = None
            if verbosity > 1:
                errors.append(entity_id + " : " + _("EntityID already exists, skipping"))
        else:
            if verbosity > 1:
                errors.append(entity_id + " : " + _("EntityID already exists, overwriting"))
    except ServiceProvider.DoesNotExist:
        if validate:
            sp = ServiceProvider.objects.create(entity_id=entity_id, service_type="saml",
                                                validated=timezone.now(), modified=False)
        else:
            sp = ServiceProvider.objects.create(entity_id=entity_id, service_type="saml",
                                                validated=None, modified=True)
        if verbosity > 2:
            errors.append(entity_id + " : " + _("EntityID does not exist, creating"))
    return sp, errors
