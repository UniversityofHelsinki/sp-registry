"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from lxml import etree, objectify
import logging
from rr.models.organization import Organization
from rr.models.nameidformat import NameIDFormat

logger = logging.getLogger(__name__)


def metadata_extensions(element, sp, privacypolicy):
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
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            PrivacyStatementURL_fi = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            PrivacyStatementURL_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            PrivacyStatementURL_fi.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"
    if sp.privacypolicy_en:
        PrivacyStatementURL_en = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        PrivacyStatementURL_en.text = sp.privacypolicy_en
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            PrivacyStatementURL_en = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            PrivacyStatementURL_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            PrivacyStatementURL_en.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"
    if sp.privacypolicy_sv:
        PrivacyStatementURL_sv = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        PrivacyStatementURL_sv.text = sp.privacypolicy_sv
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            PrivacyStatementURL_sv = etree.SubElement(UIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            PrivacyStatementURL_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            PrivacyStatementURL_sv.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"


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

    nameidformats = sp.nameidformat.all()

    for nameid in nameidformats:
        NameIDFormat = etree.SubElement(element, "NameIDFormat")
        NameIDFormat.text = nameid.nameidformat


def metadata_endpoints(element, sp, validated=True):
    """
    Generates EndPoint elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    """

    saml2_support = False
    saml1_support = False
    if validated:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    for endpoint in endpoints:
        etree.SubElement(element, endpoint.type, Binding=endpoint.binding, Location=endpoint.url)
        if endpoint.type == "AssertionConsumerService":
            if endpoint.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST":
                saml2_support = True
            if endpoint.binding == "urn:oasis:names:tc:SAML:1.0:profiles:browser-post":
                saml1_support = True
    if saml2_support and saml1_support:
        return 3
    elif saml2_support:
        return 2
    elif saml1_support:
        return 1
    else:
        return 0


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


def metadata_organization(element, sp):
    """
    Generates Organization elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    if sp.organization:
        organization = sp.organization
        Organization = etree.SubElement(element, "Organization")

        if organization.name_fi:
            DisplayName_fi = etree.SubElement(Organization, "OrganizationName")
            DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            DisplayName_fi.text = organization.name_fi
        if organization.name_en:
            DisplayName_en = etree.SubElement(Organization, "OrganizationName")
            DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            DisplayName_en.text = organization.name_en
        if organization.name_sv:
            DisplayName_sv = etree.SubElement(Organization, "OrganizationName")
            DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            DisplayName_sv.text = organization.name_sv

        if organization.description_fi:
            Description_fi = etree.SubElement(Organization, "OrganizationDisplayName")
            Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            Description_fi.text = organization.description_fi
        if organization.description_en:
            Description_en = etree.SubElement(Organization, "OrganizationDisplayName")
            Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            Description_en.text = organization.description_en
        if organization.description_sv:
            Description_sv = etree.SubElement(Organization, "OrganizationDisplayName")
            Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            Description_sv.text = organization.description_sv

        if organization.url_fi:
            OrganizationURL_fi = etree.SubElement(Organization, "OrganizationURL")
            OrganizationURL_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            OrganizationURL_fi.text = organization.url_fi
        if organization.url_en:
            OrganizationURL_en = etree.SubElement(Organization, "OrganizationURL")
            OrganizationURL_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            OrganizationURL_en.text = organization.url_en
        if organization.url_sv:
            OrganizationURL_sv = etree.SubElement(Organization, "OrganizationURL")
            OrganizationURL_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            OrganizationURL_sv.text = organization.url_sv


def metadata_spssodescriptor(element, sp, validated=True, privacypolicy=False):
    """
    Generates SPSSODescriptor elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    SPSSODescriptor = etree.SubElement(element, "SPSSODescriptor")
    if sp.sign_assertions:
        SPSSODescriptor.set("WantAssertionsSigned", "true")
    if sp.sign_requests:
        SPSSODescriptor.set("AuthnRequestsSigned", "true")
    metadata_extensions(SPSSODescriptor, sp, privacypolicy)
    metadata_certificates(SPSSODescriptor, sp, validated)
    metadata_nameidformat(SPSSODescriptor, sp)
    protocol = metadata_endpoints(SPSSODescriptor, sp, validated)
    # Set protocol support according to endpoints
    if protocol == 3:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    elif protocol == 1:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    else:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol")

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
    metadata_organization(EntityDescriptor, sp)
    metadata_contact(EntityDescriptor, sp, validated)

    return(etree.tostring(EntityDescriptor, pretty_print=True, encoding='UTF-8'))


def metadata_generator_list(serviceproviders, validated, privacypolicy):
    """
    Generates metadata for list of serviceproviders.

    sp: ServiceProvider QuerySet
    validated: if false, using unvalidated metadata
    privacypolicy: replace privacy policy if missing

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    metadata = etree.Element("EntitiesDescriptor", Name="urn:mace:funet.fi:helsinki.fi", nsmap={"xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                                                                "ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                                                                "mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
    for sp in serviceproviders:
        EntityDescriptor = etree.SubElement(metadata, "EntityDescriptor", entityID=sp.entity_id)
        metadata_spssodescriptor(EntityDescriptor, sp, validated, privacypolicy)
        metadata_contact(EntityDescriptor, sp, validated)
        metadata_organization(EntityDescriptor, sp)
    return metadata


def get_service_providers(validated=True, production=False, test=False, include=None):
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
    return serviceproviders
