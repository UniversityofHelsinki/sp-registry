"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from lxml import etree
import logging
from rr.models.organization import Organization
from rr.models.nameidformat import NameIDFormat
from django.db.models import Q

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


def metadata_certificates(element, sp, validation_date):
    """
    Generates KeyDescriptor elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    if validation_date:
        certificates = Certificate.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
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


def metadata_endpoints(element, sp, validation_date):
    """
    Generates EndPoint elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """

    saml2_support = False
    saml1_support = False
    if validation_date:
        endpoints = Endpoint.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
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


def metadata_attributeconsumingservice_meta(element, sp):
    """
    Generates AttributeConsumingService element meta for SP metadata XML

    element: etree.Element object for previous level (AttributeConsumingService)
    sp: ServiceProvider object

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    if sp.name_fi:
        DisplayName_fi = etree.SubElement(element, "ServiceName")
        DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        DisplayName_fi.text = sp.name_fi
    if sp.name_en:
        DisplayName_en = etree.SubElement(element, "ServiceName")
        DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        DisplayName_en.text = sp.name_en
    if sp.name_sv:
        DisplayName_sv = etree.SubElement(element, "ServiceName")
        DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        DisplayName_sv.text = sp.name_sv

    if sp.description_fi:
        Description_fi = etree.SubElement(element, "ServiceDescription")
        Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        Description_fi.text = sp.description_fi
    if sp.description_en:
        Description_en = etree.SubElement(element, "ServiceDescription")
        Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        Description_en.text = sp.description_en
    if sp.description_sv:
        Description_sv = etree.SubElement(element, "ServiceDescription")
        Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        Description_sv.text = sp.description_sv


def metadata_attributeconsumingservice(element, sp, history, validation_date):
    """
    Generates AttributeConsumingService element for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    history: ServiceProvider object if using validated data and most recent is not validated
    validation_date: if None, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    AttributeConsumingService = etree.SubElement(element, "AttributeConsumingService", index="1")
    if history:
        metadata_attributeconsumingservice_meta(AttributeConsumingService, history)
    else:
        metadata_attributeconsumingservice_meta(AttributeConsumingService, sp)
    if validation_date:
        attributes = SPAttribute.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
    for attribute in attributes:
        etree.SubElement(AttributeConsumingService, "RequestedAttribute",
                         FriendlyName=attribute.attribute.friendlyname, Name=attribute.attribute.name,
                         NameFormat=attribute.attribute.nameformat)


def metadata_contact(element, sp, validation_date):
    """
    Generates ContactPerson elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    if validation_date:
        contacts = Contact.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
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


def metadata_spssodescriptor(element, sp, history, validation_date, privacypolicy=False):
    """
    Generates SPSSODescriptor elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    history: ServiceProvider object if using validated data and most recent is not validated
    validation_date: if None, using unvalidated metadata
    privacypolicy: fill empty privacypolicy URLs with default value

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    SPSSODescriptor = etree.SubElement(element, "SPSSODescriptor")
    if history:
        if history.sign_assertions:
            SPSSODescriptor.set("WantAssertionsSigned", "true")
        if history.sign_requests:
            SPSSODescriptor.set("AuthnRequestsSigned", "true")
        metadata_extensions(SPSSODescriptor, history, privacypolicy)
    else:
        if sp.sign_assertions:
            SPSSODescriptor.set("WantAssertionsSigned", "true")
        if sp.sign_requests:
            SPSSODescriptor.set("AuthnRequestsSigned", "true")
        metadata_extensions(SPSSODescriptor, sp, privacypolicy)
    metadata_certificates(SPSSODescriptor, sp, validation_date)
    if history:
        metadata_nameidformat(SPSSODescriptor, history)
    else:
        metadata_nameidformat(SPSSODescriptor, sp)
    protocol = metadata_endpoints(SPSSODescriptor, sp, validation_date)
    # Set protocol support according to endpoints
    if protocol == 3:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    elif protocol == 1:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    else:
        SPSSODescriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol")

    metadata_attributeconsumingservice(SPSSODescriptor, sp, history, validation_date)


def metadata_generator(sp, validated=True, privacypolicy=False, tree=None):
    """
    Generates metadata for single SP.

    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    privacypolicy: fill empty privacypolicy URLs with default value
    tree: use as root if given, generate new root if not

    return tree

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    # Set history object if using validated metadata and newest version is not validated.
    # Set validation_date to last point where metadata was validated
    if validated and not sp.validated:
        history = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
        if not history:
            return tree
        validation_date = history.validated
    else:
        history = None
        if validated:
            validation_date = sp.validated
        else:
            validation_date = None
    if history:
        entity_id = history.entity_id
    else:
        entity_id = sp.entity_id
    if tree is not None:
        EntityDescriptor = etree.SubElement(tree, "EntityDescriptor", entityID=entity_id)
    else:
        EntityDescriptor = etree.Element("EntityDescriptor",
                                         entityID=entity_id,
                                         nsmap={"xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                "ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                "mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
    metadata_spssodescriptor(EntityDescriptor, sp, history, validation_date, privacypolicy)
    metadata_contact(EntityDescriptor, sp, validation_date)
    if history:
        metadata_organization(EntityDescriptor, history)
    else:
        metadata_organization(EntityDescriptor, sp)
    if tree is not None:
        return tree
    else:
        return EntityDescriptor


def metadata_generator_list(validated=True, privacypolicy=False, production=False, test=False, include=None):
    """
    Generates metadata for list of serviceproviders.

    validated: if false, using unvalidated metadata
    privacypolicy: replace privacy policy if missing
    production: include production SPs
    test: include test SPs
    include: include listed SPs

    return tree

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    tree = etree.Element("EntitiesDescriptor", Name="urn:mace:funet.fi:helsinki.fi", nsmap={"xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                                                            "ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                                                            "mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
    serviceproviders = ServiceProvider.objects.filter(end_at=None)
    for sp in serviceproviders:
        if production and sp.production:
            metadata_generator(sp, validated, privacypolicy, tree)
        elif test and sp.test:
            metadata_generator(sp, validated, privacypolicy, tree)
        elif include and sp.entity_id in include:
            metadata_generator(sp, validated, privacypolicy, tree)
    return tree
