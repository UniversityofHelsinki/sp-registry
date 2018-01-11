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


def metadata_generator(sp):
    """
    Using CamelCase instead of regular underscore attribute names in element tree.
    Generates metadata for single SP.
    """
    basicinfo = sp
    certificates = Certificate.objects.filter(sp=sp, end_at=None)
    contacts = Contact.objects.filter(sp=sp, end_at=None)
    endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    attributes = SPAttribute.objects.filter(sp=sp)

    EntityDescriptor = etree.Element("EntityDescriptor",
                                     schemaLocation="urn:oasis:names:tc:SAML:2.0:metadata",
                                     entityID=basicinfo.entity_id)
    SPSSODescriptor = etree.SubElement(EntityDescriptor, "SPSSODescriptor", protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol")
    Extensions = etree.SubElement(SPSSODescriptor, "Extensions")
    if basicinfo.discovery_service_url:
        DiscoveryResponse = etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol}DiscoveryResponse",
                                             Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol",
                                             Location=basicinfo.discovery_service_url,
                                             index="1",
                                             nsmap={"idpdisc": 'urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol'})
    UIIInfo = etree.SubElement(Extensions, "{urn:oasis:names:tc:SAML:metadata:ui}UIIInfo",
                               nsmap={"mdui": 'urn:oasis:names:tc:SAML:metadata:ui'})
    if basicinfo.name_fi:
        DisplayName_fi = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        DisplayName_fi.text = basicinfo.name_fi
    if basicinfo.name_en:
        DisplayName_en = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        DisplayName_en.text = basicinfo.name_en
    if basicinfo.name_sv:
        DisplayName_sv = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}DisplayName")
        DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        DisplayName_sv.text = basicinfo.name_sv

    if basicinfo.description_fi:
        Description_fi = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        Description_fi.text = basicinfo.description_fi
    if basicinfo.description_en:
        Description_en = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        Description_en.text = basicinfo.description_en
    if basicinfo.description_sv:
        Description_sv = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}Description")
        Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        Description_sv.text = basicinfo.description_sv

    if basicinfo.privacypolicy_fi:
        PrivacyStatementURL_fi = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        PrivacyStatementURL_fi.text = basicinfo.privacypolicy_fi
    if basicinfo.privacypolicy_en:
        PrivacyStatementURL_en = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        PrivacyStatementURL_en.text = basicinfo.privacypolicy_en
    if basicinfo.privacypolicy_sv:
        PrivacyStatementURL_sv = etree.SubElement(UIIInfo, "{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL")
        PrivacyStatementURL_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        PrivacyStatementURL_sv.text = basicinfo.privacypolicy_sv

    for certificate in certificates:
        KeyDescriptor = etree.SubElement(SPSSODescriptor, "KeyDescriptor")
        if certificate.signing:
            KeyDescriptor.attrib['use'] = 'signing'
        if certificate.encryption:
            KeyDescriptor.attrib['use'] = 'encryption'

        KeyInfo = etree.SubElement(KeyDescriptor, "{urn:oasis:names:tc:SAML:2.0:metadata}KeyInfo",
                                   nsmap={"ds": 'urn:oasis:names:tc:SAML:2.0:metadata'})
        X509Data = etree.SubElement(KeyInfo, "{urn:oasis:names:tc:SAML:2.0:metadata}X509Data")
        X509Certificate = etree.SubElement(X509Data, "{urn:oasis:names:tc:SAML:2.0:metadata}X509Certificate")
        X509Certificate.text = certificate.get_certificate_content()

    if basicinfo.name_format_transient:
        NameIDFormat = etree.SubElement(SPSSODescriptor, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    if basicinfo.name_format_persistent:
        NameIDFormat = etree.SubElement(SPSSODescriptor, "NameIDFormat")
        NameIDFormat.text = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"

    for endpoint in endpoints:
        etree.SubElement(SPSSODescriptor, endpoint.type, Binding=endpoint.binding, Location=endpoint.url)

    AttributeConsumingService = etree.SubElement(SPSSODescriptor, "AttributeConsumingService", index="1")
    if basicinfo.name_fi:
        DisplayName_fi = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        DisplayName_fi.text = basicinfo.name_fi
    if basicinfo.name_en:
        DisplayName_en = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        DisplayName_en.text = basicinfo.name_en
    if basicinfo.name_sv:
        DisplayName_sv = etree.SubElement(AttributeConsumingService, "ServiceName")
        DisplayName_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        DisplayName_sv.text = basicinfo.name_sv

    if basicinfo.description_fi:
        Description_fi = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_fi.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fi"
        Description_fi.text = basicinfo.description_fi
    if basicinfo.description_en:
        Description_en = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_en.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
        Description_en.text = basicinfo.description_en
    if basicinfo.description_sv:
        Description_sv = etree.SubElement(AttributeConsumingService, "ServiceDescription")
        Description_sv.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "sv"
        Description_sv.text = basicinfo.description_sv

    for attribute in attributes:
        etree.SubElement(AttributeConsumingService, "RequestedAttribute",
                         FriendlyName=attribute.attribute.friendlyname, Name=attribute.attribute.name,
                         NameFormat=attribute.attribute.nameformat)

    for contact in contacts:
        ContactPerson = etree.SubElement(EntityDescriptor, "ContactPerson", contactType=contact.type)
        GivenName = etree.SubElement(ContactPerson, "GivenName")
        GivenName.text = contact.firstname
        SurName = etree.SubElement(ContactPerson, "SurName")
        SurName.text = contact.lastname
        EmailAddress = etree.SubElement(ContactPerson, "EmailAddress")
        EmailAddress.text = contact.email

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
        raise Http404("Service proviced does not exist")
    metadata = metadata_generator(sp)
    return render(request, "rr/metadata.html", {'object': sp,
                                                'metadata': metadata})
