"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from lxml import etree, objectify


def metadata_extensions(element, sp):
    Extensions = etree.SubElement(element, "Extensions")
    if sp.discovery_service_url:
        etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol}DiscoveryResponse",
                         Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol",
                         Location=sp.discovery_service_url,
                         index="1",
                         nsmap={"idpdisc": 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol'})
    UIInfo = etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:metadata:ui}UIInfo",
                              nsmap={"mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
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
    if validated:
        certificates = Certificate.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        certificates = Certificate.objects.filter(sp=sp, end_at=None)
    for certificate in certificates:
        KeyDescriptor = etree.SubElement(element, "KeyDescriptor",
                                         nsmap={"ds": 'urn:oasis:names:tc:SAML:2.0:metadata'})
        if certificate.signing and not certificate.encryption:
            KeyDescriptor.attrib['use'] = 'signing'
        if certificate.encryption and not certificate.signing:
            KeyDescriptor.attrib['use'] = 'encryption'

        KeyInfo = etree.SubElement(KeyDescriptor, "{urn:oasis:names:tc:SAML:2.0:metadata}KeyInfo",
                                   nsmap={"ds": 'urn:oasis:names:tc:SAML:2.0:metadata'})
        X509Data = etree.SubElement(KeyInfo, "{urn:oasis:names:tc:SAML:2.0:metadata}X509Data")
        X509Certificate = etree.SubElement(X509Data, "{urn:oasis:names:tc:SAML:2.0:metadata}X509Certificate")
        X509Certificate.text = certificate.certificate


def metadata_nameidformat(element, sp):
    if sp.name_format_transient:
        NameIDFormat = etree.SubElement(element, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    if sp.name_format_persistent:
        NameIDFormat = etree.SubElement(element, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"


def metadata_endpoints(element, sp, validated=True):
    if validated:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None).exclude(validated=None)
    else:
        endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    for endpoint in endpoints:
        etree.SubElement(element, endpoint.type, Binding=endpoint.binding, Location=endpoint.url)


def metadata_attributeconsumingservice(element, sp, validated=True):
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
    SPSSODescriptor = etree.SubElement(element, "SPSSODescriptor", protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol")
    metadata_extensions(SPSSODescriptor, sp)
    metadata_certificates(SPSSODescriptor, sp, validated)
    metadata_nameidformat(SPSSODescriptor, sp)
    metadata_endpoints(SPSSODescriptor, sp, validated)
    metadata_attributeconsumingservice(SPSSODescriptor, sp, validated)


def metadata_generator(sp, validated=True):
    """
    Using CamelCase instead of regular underscore attribute names in element tree.
    Generates metadata for single SP.
    """

    EntityDescriptor = etree.Element("EntityDescriptor",
                                     schemaLocation="urn:oasis:names:tc:SAML:2.0:metadata",
                                     entityID=sp.entity_id)
    metadata_spssodescriptor(EntityDescriptor, sp, validated)
    metadata_contact(EntityDescriptor, sp, validated)

    return(etree.tostring(EntityDescriptor, pretty_print=True))


@login_required
def metadata(request, pk):
    """
    Displays a metadata for :model:`rr.ServiceProvider`.

    **Context**

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    ``metadata``
        Metadata for a :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/metadata.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service provider does not exist")
    if request.GET.get('validated', '') in ("false", "False"):
        validated = False
    else:
        validated = True
    metadata_sp = sp
    if validated and not sp.validated:
        metadata_sp = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
    if metadata_sp:
        metadata = metadata_generator(sp=metadata_sp, validated=validated)
    else:
        metadata = None
    return render(request, "rr/metadata.html", {'object': sp,
                                                'metadata': metadata,
                                                'validated': validated})
