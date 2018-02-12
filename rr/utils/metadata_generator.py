"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import SPAttribute
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from lxml import etree, objectify
import logging

logger = logging.getLogger(__name__)


def metadata_extensions(element, sp):
    """
    Generates Extensions element for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    Extensions = etree.SubElement(element, "Extensions")
    if sp.discovery_service_url:
        etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol}DiscoveryResponse",
                         Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol",
                         Location=sp.discovery_service_url,
                         index="1",
                         nsmap={"idpdisc": 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol'})
    UIInfo = etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:metadata:ui}UIInfo")
    if sp.name_fi:
        DisplayName_fi = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        DisplayName_fi.text = sp.name_fi
    if sp.name_en:
        DisplayName_en = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        DisplayName_en.text = sp.name_en
    if sp.name_sv:
        DisplayName_sv = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        DisplayName_sv.text = sp.name_sv

    if sp.description_fi:
        Description_fi = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        Description_fi.text = sp.description_fi
    if sp.description_en:
        Description_en = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        Description_en.text = sp.description_en
    if sp.description_sv:
        Description_sv = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        Description_sv.text = sp.description_sv

    if sp.privacypolicy_fi:
        PrivacyStatementURL_fi = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        PrivacyStatementURL_fi.text = sp.privacypolicy_fi
    if sp.privacypolicy_en:
        PrivacyStatementURL_en = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        PrivacyStatementURL_en.text = sp.privacypolicy_en
    if sp.privacypolicy_sv:
        PrivacyStatementURL_sv = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        PrivacyStatementURL_sv.text = sp.privacypolicy_sv


def metadata_certificates(element, sp, validated=True):
    """
    Generates KeyDescriptor elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    if validated:
        certificates = Certificate.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        certificates = Certificate.objects.filter(sp=sp, end_at=None)
    for certificate in certificates:
        KeyDescriptor = etree.SubElement(element, "KeyDescriptor")
        if certificate.signing and not certificate.encryption:
            KeyDescriptor.attrib['use'] = 'signing'
        if certificate.encryption and not certificate.signing:
            KeyDescriptor.attrib['use'] = 'encryption'

        KeyInfo = etree.SubElement(KeyDescriptor, "{http://www.w3.org/2000/09/xmldsig#}KeyInfo")
        X509Data = etree.SubElement(KeyInfo, "{http://www.w3.org/2000/09/xmldsig#}X509Data")
        X509Certificate = etree.SubElement(X509Data, "{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
        X509Certificate.text = certificate.certificate


def metadata_nameidformat(element, sp):
    """
    Generates NameIDFormat elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    """

    if sp.name_format_transient:
        NameIDFormat = etree.SubElement(element, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    if sp.name_format_persistent:
        NameIDFormat = etree.SubElement(element, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"


def metadata_endpoints(element, sp, validated=True):
    """
    Generates EndPoint elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    """

    if validated:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    for endpoint in endpoints:
        etree.SubElement(element, endpoint.type, Binding=endpoint.binding, Location=endpoint.url)


def metadata_attributeconsumingservice(element, sp, validated=True):
    """
    Generates AttributeConsumingService element for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    if validated:
        attributes = SPAttribute.objects.filter(sp=sp).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp)
    AttributeConsumingService = etree.SubElement(element, "AttributeConsumingService", index="1")
    if sp.name_fi:
        DisplayName_fi = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        DisplayName_fi.text = sp.name_fi
    if sp.name_en:
        DisplayName_en = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        DisplayName_en.text = sp.name_en
    if sp.name_sv:
        DisplayName_sv = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        DisplayName_sv.text = sp.name_sv

    if sp.description_fi:
        Description_fi = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        Description_fi.text = sp.description_fi
    if sp.description_en:
        Description_en = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        Description_en.text = sp.description_en
    if sp.description_sv:
        Description_sv = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        Description_sv.text = sp.description_sv

    for attribute in attributes:
        etree.SubElement(AttributeConsumingService, "RequestedAttribute",
                         FriendlyName=attribute.attribute.friendlyname, Name=attribute.attribute.name,
                         NameFormat=attribute.attribute.nameformat)


def metadata_contact(element, sp, validated=True):
    """
    Generates ContactPerson elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    if validated:
        contacts = Contact.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        contacts = Contact.objects.filter(sp=sp, end_at=None)
    for contact in contacts:
        ContactPerson = etree.SubElement(element, "ContactPerson", contactType=contact.type)
        GivenName = etree.SubElement(ContactPerson, "GivenName")
        GivenName.text = contact.firstname
        SurName = etree.SubElement(ContactPerson, "SurName")
        SurName.text = contact.lastname
        EmailAddress = etree.SubElement(ContactPerson, "EmailAddress")
        EmailAddress.text = contact.email


def metadata_spssodescriptor(element, sp, validated=True):
    """
    Generates SPSSODescriptor elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    SPSSODescriptor = etree.SubElement(element, "SPSSODescriptor", protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol")
    metadata_extensions(SPSSODescriptor, sp)
    metadata_certificates(SPSSODescriptor, sp, validated)
    metadata_nameidformat(SPSSODescriptor, sp)
    metadata_endpoints(SPSSODescriptor, sp, validated)
    metadata_attributeconsumingservice(SPSSODescriptor, sp, validated)


def metadata_generator(sp, validated=True):
    """
    Generates metadata for single SP.

    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    EntityDescriptor = etree.Element("EntityDescriptor",
                                     schemaLocation="urn:oasis:names:tc:SAML:2.0:metadata",
                                     entityID=sp.entity_id,
                                     nsmap={"ds": 'http://www.w3.org/2000/09/xmldsig#',
                                            "mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
    metadata_spssodescriptor(EntityDescriptor, sp, validated)
    metadata_contact(EntityDescriptor, sp, validated)

    return(etree.tostring(EntityDescriptor, pretty_print=True, encoding='UTF-8'))