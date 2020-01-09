"""
Functions for genereating metadata of service providers
"""

import logging

from lxml import etree

from django.conf import settings
from django.db.models import Q

from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.utils.metadata_generator_common import get_entity

logger = logging.getLogger(__name__)


def metadata_spssodescriptor_extensions(element, sp, privacypolicy):
    """
    Generates Extensions element for SP SSO Descriptor metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    privacypolicy: fill empty privacypolicy URLs with default value
    """

    extensions = etree.SubElement(element, "Extensions")
    if sp.discovery_service_url:
        etree.SubElement(extensions, "{urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol}DiscoveryResponse",
                         Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol",
                         Location=sp.discovery_service_url,
                         index="1",
                         nsmap={"idpdisc": 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol'})
    if sp.login_page_url:
        etree.SubElement(extensions, "{urn:oasis:names:tc:SAML:profiles:SSO:request-init}RequestInitiator",
                         Binding="urn:oasis:names:tc:SAML:profiles:SSO:request-init",
                         Location=sp.login_page_url,
                         nsmap={"init": 'urn:oasis:names:tc:SAML:profiles:SSO:request-init'})

    ui_info = etree.SubElement(extensions, "{urn:oasis:names:tc:SAML:metadata:ui}UIInfo")
    if sp.name_fi:
        display_name_fi = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        display_name_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        display_name_fi.text = sp.name_fi
    if sp.name_en:
        display_name_en = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        display_name_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        display_name_en.text = sp.name_en
    if sp.name_sv:
        display_name_sv = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        display_name_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        display_name_sv.text = sp.name_sv

    if sp.description_fi:
        description_fi = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        description_fi.text = sp.description_fi
    if sp.description_en:
        description_en = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        description_en.text = sp.description_en
    if sp.description_sv:
        description_sv = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        description_sv.text = sp.description_sv

    if sp.privacypolicy_fi:
        privacy_statement_url_fi = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        privacy_statement_url_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        privacy_statement_url_fi.text = sp.privacypolicy_fi
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            privacy_statement_url_fi = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            privacy_statement_url_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            privacy_statement_url_fi.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"
    if sp.privacypolicy_en:
        privacy_statement_url_en = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        privacy_statement_url_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        privacy_statement_url_en.text = sp.privacypolicy_en
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            privacy_statement_url_en = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            privacy_statement_url_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            privacy_statement_url_en.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"
    if sp.privacypolicy_sv:
        privacy_statement_url_sv = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        privacy_statement_url_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        privacy_statement_url_sv.text = sp.privacypolicy_sv
    else:
        if sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
            privacy_statement_url_sv = etree.SubElement(ui_info, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
            privacy_statement_url_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            privacy_statement_url_sv.text = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet-0"
    if len(ui_info) == 0:
        extensions.remove(ui_info)
    if len(extensions) == 0:
        element.remove(extensions)


def metadata_entity_extensions(element, sp):
    """
    Generates Extensions element for SP EntityDescriptor metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    """

    extensions = etree.SubElement(element, "Extensions")
    entity_attributes = etree.SubElement(extensions, "{urn:oasis:names:tc:SAML:metadata:attribute}EntityAttributes")
    if not sp.sign_responses:
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/signResponses",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "xsd:boolean"
        attribute_value.text = "false"
    if not sp.encrypt_assertions:
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/encryptAssertions",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "xsd:boolean"
        attribute_value.text = "false"
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/encryptNameIDs",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = "xsd:boolean"
        attribute_value.text = "false"
    if sp.force_sha1:
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/securityConfiguration",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.text = "shibboleth.SecurityConfiguration.SHA1"
    if sp.force_mfa and hasattr(settings, 'MFA_AUTHENTICATION_CONTEXT') and settings.MFA_AUTHENTICATION_CONTEXT:
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/defaultAuthenticationMethods",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.text = settings.MFA_AUTHENTICATION_CONTEXT
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/disallowedFeatures",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.text = "0x1"
    if sp.force_nameidformat and len(sp.nameidformat.all()) == 1:
        attribute = etree.SubElement(entity_attributes, "{urn:oasis:names:tc:SAML:2.0:assertion}Attribute",
                                     Name="http://shibboleth.net/ns/profiles/nameIDFormatPrecedence",
                                     NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
        attribute_value = etree.SubElement(attribute, "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue")
        attribute_value.text = sp.nameidformat.all()[0].nameidformat
    if len(entity_attributes) == 0:
        extensions.remove(entity_attributes)
        element.remove(extensions)


def metadata_certificates(element, sp, validation_date):
    """
    Generates KeyDescriptor elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """
    if validation_date:
        certificates = Certificate.objects.filter(
            sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        certificates = Certificate.objects.filter(sp=sp, end_at=None)
    for certificate in certificates:
        key_descriptor = etree.SubElement(element, "KeyDescriptor")
        if certificate.signing and not certificate.encryption:
            key_descriptor.attrib['use'] = 'signing'
        if certificate.encryption and not certificate.signing:
            key_descriptor.attrib['use'] = 'encryption'

        key_info = etree.SubElement(key_descriptor, "{http://www.w3.org/2000/09/xmldsig#}KeyInfo")
        x509_data = etree.SubElement(key_info, "{http://www.w3.org/2000/09/xmldsig#}X509Data")
        x509_certificate = etree.SubElement(x509_data, "{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
        x509_certificate.text = certificate.certificate


def metadata_nameidformat(element, sp):
    """
    Generates NameIDFormat elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    """

    nameidformats = sp.nameidformat.all()

    for nameid in nameidformats:
        name_id_format = etree.SubElement(element, "NameIDFormat")
        name_id_format.text = nameid.nameidformat


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
        endpoints = Endpoint.objects.filter(sp=sp).filter(Q(end_at=None) |
                                                          Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    for endpoint in endpoints:
        subelement = etree.SubElement(element, endpoint.type, Binding=endpoint.binding, Location=endpoint.location)
        if endpoint.response_location:
            subelement.set('ResponseLocation', endpoint.response_location)
        if endpoint.index:
            subelement.set('index', str(endpoint.index))
        if endpoint.is_default:
            subelement.set('isDefault', "true")
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
    """
    if sp.name_fi:
        display_name_fi = etree.SubElement(element, "ServiceName")
        display_name_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        display_name_fi.text = sp.name_fi
    if sp.name_en:
        display_name_en = etree.SubElement(element, "ServiceName")
        display_name_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        display_name_en.text = sp.name_en
    if sp.name_sv:
        display_name_sv = etree.SubElement(element, "ServiceName")
        display_name_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        display_name_sv.text = sp.name_sv

    if sp.description_fi:
        description_fi = etree.SubElement(element, "ServiceDescription")
        description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        description_fi.text = sp.description_fi
    if sp.description_en:
        description_en = etree.SubElement(element, "ServiceDescription")
        description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        description_en.text = sp.description_en
    if sp.description_sv:
        description_sv = etree.SubElement(element, "ServiceDescription")
        description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        description_sv.text = sp.description_sv


def metadata_attributeconsumingservice(element, sp, history, validation_date):
    """
    Generates AttributeConsumingService element for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    history: ServiceProvider object if using validated data and most recent is not validated
    validation_date: if None, using unvalidated metadata
    """
    attribute_consuming_service = etree.SubElement(element, "AttributeConsumingService", index="1")
    if history:
        metadata_attributeconsumingservice_meta(attribute_consuming_service, history)
    else:
        metadata_attributeconsumingservice_meta(attribute_consuming_service, sp)
    if validation_date:
        attributes = SPAttribute.objects.filter(sp=sp).filter(Q(end_at=None) |
                                                              Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
    for attribute in attributes:
        etree.SubElement(attribute_consuming_service, "RequestedAttribute",
                         FriendlyName=attribute.attribute.friendlyname, Name=attribute.attribute.name,
                         NameFormat=attribute.attribute.nameformat)
    if len(attribute_consuming_service) == 0:
        element.remove(attribute_consuming_service)


def metadata_contact(element, sp, validation_date):
    """
    Generates ContactPerson elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """

    if validation_date:
        contacts = Contact.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        contacts = Contact.objects.filter(sp=sp, end_at=None)
    for contact in contacts:
        contact_person = etree.SubElement(element, "ContactPerson", contactType=contact.type)
        given_name = etree.SubElement(contact_person, "GivenName")
        given_name.text = contact.firstname
        sur_name = etree.SubElement(contact_person, "SurName")
        sur_name.text = contact.lastname
        email_address = etree.SubElement(contact_person, "EmailAddress")
        email_address.text = contact.email


def metadata_organization(element, sp):
    """
    Generates Organization elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    """

    if sp.organization:
        organization = sp.organization
        organization_element = etree.SubElement(element, "Organization")

        if organization.name_fi:
            display_name_fi = etree.SubElement(organization_element, "OrganizationName")
            display_name_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            display_name_fi.text = organization.name_fi
        if organization.name_en:
            display_name_en = etree.SubElement(organization_element, "OrganizationName")
            display_name_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            display_name_en.text = organization.name_en
        if organization.name_sv:
            display_name_sv = etree.SubElement(organization_element, "OrganizationName")
            display_name_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            display_name_sv.text = organization.name_sv

        if organization.description_fi:
            description_fi = etree.SubElement(organization_element, "OrganizationDisplayName")
            description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            description_fi.text = organization.description_fi
        if organization.description_en:
            description_en = etree.SubElement(organization_element, "OrganizationDisplayName")
            description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            description_en.text = organization.description_en
        if organization.description_sv:
            description_sv = etree.SubElement(organization_element, "OrganizationDisplayName")
            description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            description_sv.text = organization.description_sv

        if organization.url_fi:
            organization_url_fi = etree.SubElement(organization_element, "OrganizationURL")
            organization_url_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
            organization_url_fi.text = organization.url_fi
        if organization.url_en:
            organization_url_en = etree.SubElement(organization_element, "OrganizationURL")
            organization_url_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
            organization_url_en.text = organization.url_en
        if organization.url_sv:
            organization_url_sv = etree.SubElement(organization_element, "OrganizationURL")
            organization_url_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
            organization_url_sv.text = organization.url_sv


def metadata_spssodescriptor(element, sp, history, validation_date, privacypolicy=False):
    """
    Generates SPSSODescriptor elements for SP metadata XML

    element: etree.Element object for previous level (EntityDescriptor)
    sp: ServiceProvider object
    history: ServiceProvider object if using validated data and most recent is not validated
    validation_date: if None, using unvalidated metadata
    privacypolicy: fill empty privacypolicy URLs with default value
    """

    sp_sso_descriptor = etree.SubElement(element, "SPSSODescriptor")
    if history:
        if history.sign_assertions:
            sp_sso_descriptor.set("WantAssertionsSigned", "true")
        if history.sign_requests:
            sp_sso_descriptor.set("AuthnRequestsSigned", "true")
        metadata_spssodescriptor_extensions(sp_sso_descriptor, history, privacypolicy)
    else:
        if sp.sign_assertions:
            sp_sso_descriptor.set("WantAssertionsSigned", "true")
        if sp.sign_requests:
            sp_sso_descriptor.set("AuthnRequestsSigned", "true")
        metadata_spssodescriptor_extensions(sp_sso_descriptor, sp, privacypolicy)
    metadata_certificates(sp_sso_descriptor, sp, validation_date)
    if history:
        metadata_nameidformat(sp_sso_descriptor, history)
    else:
        metadata_nameidformat(sp_sso_descriptor, sp)
    protocol = metadata_endpoints(sp_sso_descriptor, sp, validation_date)
    # Set protocol support according to endpoints
    if protocol == 3:
        sp_sso_descriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    elif protocol == 1:
        sp_sso_descriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:1.1:protocol urn:oasis:names:tc:SAML:1.0:protocol")
    else:
        sp_sso_descriptor.set("protocolSupportEnumeration", "urn:oasis:names:tc:SAML:2.0:protocol")

    metadata_attributeconsumingservice(sp_sso_descriptor, sp, history, validation_date)


def saml_metadata_generator(sp, validated=True, privacypolicy=False, tree=None, disable_entity_extensions=False):
    """
    Generates metadata for single SP.

    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    privacypolicy: fill empty privacypolicy URLs with default value
    tree: use as root if given, generate new root if not

    return tree
    """
    entity, history, validation_date = get_entity(sp, validated)
    if not entity:
        return tree
    if tree is not None:
        entity_descriptor = etree.SubElement(tree, "EntityDescriptor", entityID=entity.entity_id)
    else:
        entity_descriptor = etree.Element("EntityDescriptor",
                                          entityID=entity.entity_id,
                                          nsmap={"ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                 "mdattr": 'urn:oasis:names:tc:SAML:metadata:attribute',
                                                 "mdui": 'urn:oasis:names:tc:SAML:metadata:ui',
                                                 "saml": 'urn:oasis:names:tc:SAML:2.0:assertion',
                                                 "xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                 "xsd": 'http://www.w3.org/2001/XMLSchema',
                                                 "xsi": 'http://www.w3.org/2001/XMLSchema-instance',
                                                 })
    if not disable_entity_extensions:
        if history:
            metadata_entity_extensions(entity_descriptor, history)
        else:
            metadata_entity_extensions(entity_descriptor, sp)
    metadata_spssodescriptor(entity_descriptor, sp, history, validation_date, privacypolicy)
    metadata_contact(entity_descriptor, sp, validation_date)
    if history:
        metadata_organization(entity_descriptor, history)
    else:
        metadata_organization(entity_descriptor, sp)
    if tree is not None:
        return tree
    else:
        return entity_descriptor


def saml_metadata_generator_list(validated=True, privacypolicy=False, production=False, test=False, include=None,
                                 as_list=False):
    """
    Generates metadata for list of serviceproviders.

    validated: if false, using unvalidated metadata
    privacypolicy: replace privacy policy if missing
    production: include production SPs
    test: include test SPs
    include: include listed SPs
    as_list: return metadata as list of individual metadata instead etree object

    return tree
    """
    tree = etree.Element("EntitiesDescriptor", Name="urn:mace:funet.fi:helsinki.fi", nsmap={"ds": 'http://www.w3.org/2000/09/xmldsig#',
                                                                                            "mdattr": 'urn:oasis:names:tc:SAML:metadata:attribute',
                                                                                            "mdui": 'urn:oasis:names:tc:SAML:metadata:ui',
                                                                                            "saml": 'urn:oasis:names:tc:SAML:2.0:assertion',
                                                                                            "xmlns": 'urn:oasis:names:tc:SAML:2.0:metadata',
                                                                                            "xsd": 'http://www.w3.org/2001/XMLSchema',
                                                                                            "xsi": 'http://www.w3.org/2001/XMLSchema-instance',
                                                                                            })
    metadata_list = []
    serviceproviders = ServiceProvider.objects.filter(end_at=None, service_type="saml")
    if hasattr(settings, 'DISABLE_METADATA_ENTITY_EXTENSIONS') and settings.DISABLE_METADATA_ENTITY_EXTENSIONS:
        disable_entity_extensions = True
    else:
        disable_entity_extensions = False
    for sp in serviceproviders:
        if (production and sp.production) or (test and sp.test) or (include and sp.entity_id in include):
            if as_list:
                metadata_list.append(
                    saml_metadata_generator(sp, validated, privacypolicy, None, disable_entity_extensions))
            else:
                saml_metadata_generator(sp, validated, privacypolicy, tree, disable_entity_extensions)
    if as_list:
        return metadata_list
    else:
        return tree
