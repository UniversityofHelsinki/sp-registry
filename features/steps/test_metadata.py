from behave import when, then

from django.core.management import call_command
from django.utils.six import StringIO


@when(u'loading test metadata')
def load_test_metadata(context):
    out = StringIO()
    call_command('importmetadata', '-i', 'rr/testdata/metadata.xml', '-a', stdout=out)


@then(u'the page will have same metadata')
def check_for_text(context):
    assert context.browser.is_text_present("""<EntityDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:mdattr="urn:oasis:names:tc:SAML:metadata:attribute" xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" entityID="https://sp.example.org/sp">
  <SPSSODescriptor AuthnRequestsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <Extensions>
      <mdui:UIInfo>
        <mdui:DisplayName xml:lang="fi">Testiohjelma</mdui:DisplayName>
        <mdui:DisplayName xml:lang="en">Test application</mdui:DisplayName>
        <mdui:DisplayName xml:lang="sv">Testapplikation</mdui:DisplayName>
        <mdui:Description xml:lang="fi">Testimetadata resurssirekisteriin</mdui:Description>
        <mdui:Description xml:lang="en">Testing metadata for resource registry</mdui:Description>
        <mdui:Description xml:lang="sv">Testa metadata för resursregistret</mdui:Description>
        <mdui:PrivacyStatementURL xml:lang="fi">https://sp.example.org/privacy/policy_fi.pdf</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="en">https://sp.example.org/privacy/policy_en.pdf</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="sv">https://sp.example.org/privacy/policy_ev.pdf</mdui:PrivacyStatementURL>
      </mdui:UIInfo>
    </Extensions>
    <KeyDescriptor>
      <ds:KeyInfo>
        <ds:X509Data>
          <ds:X509Certificate>MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
BAMMDnNwLmV4YW1wbGUub3JnMB4XDTE4MDExNjExMTAxN1oXDTI4MDExNDExMTAx
N1owGTEXMBUGA1UEAwwOc3AuZXhhbXBsZS5vcmcwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDlomqiyCbu1nKL9BtTwFjuNr0O2iDrQ1DbOnMu6E3tg0CO
kvmxzy7e9RuVzJUzz4bCz5u7xoHAFzaOX/k0FwRp32k9//4KNiioZta+sOE5ewyi
9ooOxqYtBMC7xy4AF/+7U2XoeGvdPPswUjEB0b312K4Xu3tvQy4ZdDhIiIHizLng
bHOUX8Isq50z8PmSEPE/DMMfK4mvfSMT067fC6tX+WHjlb8PHgEBn09f8kL76+x6
JLm6uGPN2M0lL1mtoN3lumYxldifsf2REuZdVSQYGRqQWjvMDJCPy1NRyvUHRDRr
FWIgEJhSpp0PdLd+9oK4Wccw8L2PN/khpXAJAVrAuMrOzASWL+ZuCQbUHSoK0Asb
4eN5jgDBNU63P/Ev4//JaUwNmYWMSeqEEKzun0WansZFC2LUkVjvuSZ2JV4bzu+s
pRdj0dkEa5HOhk7Bvd/eN0h2aVLsF3EgXekDudbKXMwQOxrazJoVHv9pwxsZxlHK
LP298175K/skR8VASQdH3JBrXpdiDb4mLoyXdx/I11Tx13fuiQogIRcm6ccqy/Ob
1nFzh1tkqTaFJF2F3cLCpbrqv853vWC08bRACkIeJQ8R8EDJudvk3cQllHHfItss
yoR//TcHJXsu+zwTruW6wdLkXShG3v2N2zplChuUczFYOT1FjZa+hRhk8p6tOwID
AQABo1AwTjAdBgNVHQ4EFgQU2TjrYXoZH0JkPA3YIZe+H0v1jqcwHwYDVR0jBBgw
FoAU2TjrYXoZH0JkPA3YIZe+H0v1jqcwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAgEAJUjWKsLdtVI5xqfi7RLk1viyTdvKi2sTkXgKySNPffwRLoEcmIAp
FPX0TAhsoBdxE7OFwlSmb6ZX89CtNlwyyVHlWemwgKNfjdgj0qkk7Lreq+L1si6j
diml6uFfMbZrHtppxHENDYckxxfD3Zooa/pY9NUG17BHzoNTAsDhFq7YCA4Y2j6h
acYh1pa0PQ4rhE2zhFs3AZF+gaYGdwtKEcJBEQ6OcctP3Y8K/FTDmJAK3dERdmrh
BdeYSRTQSQMm0W1SsIsEMEfndC1Cca/aKrl8B1tZz55s04WPx/e92NV9S5KGRH0G
UADycvLo12NUfqubK+2+bcH92rhHZ1QGjkfJmHwhXIqt8F1gysQQO+M3uYhlpiIR
4vQBWFqoMCT7lqQYj1tCvrt6+RVv3Zz8t0eMfJXSFAoJPbjv3npPcUfjmLRG7W9y
VSb6gzk3PYRVB0NzmlPdB4KFdBQbsuE8qoPr3UBbHIiD9wFU6K6eUZkIjqIV/5az
56c2mntFDpdx+46RkS/7CEAbZkD8kEM5vrhpDXhbfLzIDTnOTBTbrwGmPCnpYSXy
rKLt+NcwtbkI6weLISJu9lFZnPMYT7LpqDWD4aMHHUWr8THO0T6mbCeQRYMlfSpU
0es8zIhYt2fRbxHFRIFyRZYJrQoSfkU5OMas/ypz/q2wOvgqjH8qyRQ=
</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://sp.example.org/Shibboleth.sso/SAML2/POST"/>
    <SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://sp.example.org/Shibboleth.sso/SAML2/Redirect"/>
    <AttributeConsumingService index="1">
      <ServiceName xml:lang="fi">Testiohjelma</ServiceName>
      <ServiceName xml:lang="en">Test application</ServiceName>
      <ServiceName xml:lang="sv">Testapplikation</ServiceName>
      <ServiceDescription xml:lang="fi">Testimetadata resurssirekisteriin</ServiceDescription>
      <ServiceDescription xml:lang="en">Testing metadata for resource registry</ServiceDescription>
      <ServiceDescription xml:lang="sv">Testa metadata för resursregistret</ServiceDescription>
      <RequestedAttribute FriendlyName="mail" Name="urn:oid:0.9.2342.19200300.100.1.3" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
      <RequestedAttribute FriendlyName="schacPersonalUniqueCode" Name="urn:oid:1.3.6.1.4.1.25178.1.2.14" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
    </AttributeConsumingService>
  </SPSSODescriptor>
  <ContactPerson contactType="administrative">
    <GivenName>John</GivenName>
    <SurName>Doe</SurName>
    <EmailAddress>john.doe@example.org</EmailAddress>
  </ContactPerson>
  <ContactPerson contactType="technical">
    <GivenName>Jane</GivenName>
    <SurName>Doe</SurName>
    <EmailAddress>jane.doe@example.org</EmailAddress>
  </ContactPerson>
</EntityDescriptor>""")


@then(u'the page will have default metadata')
def check_for_default_metadata(context):
    assert context.browser.is_text_present("""<EntityDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:mdattr="urn:oasis:names:tc:SAML:metadata:attribute" xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" entityID="https://sp.example.org/sp">
  <SPSSODescriptor AuthnRequestsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <Extensions>
      <idpdisc:DiscoveryResponse xmlns:idpdisc="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Location="https://discovery.example.org/" index="1"/>
      <init:RequestInitiator xmlns:init="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Binding="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Location="https://corp.example.org/login/"/>
      <mdui:UIInfo>
        <mdui:DisplayName xml:lang="fi">Mun ohjelma</mdui:DisplayName>
        <mdui:DisplayName xml:lang="en">My program name</mdui:DisplayName>
        <mdui:DisplayName xml:lang="sv">Mitt program</mdui:DisplayName>
        <mdui:Description xml:lang="fi">Tämän palvelun testaus</mdui:Description>
        <mdui:Description xml:lang="en">Testing this service</mdui:Description>
        <mdui:Description xml:lang="sv">Testa denna tjänst</mdui:Description>
        <mdui:PrivacyStatementURL xml:lang="fi">https://corp.example.org/privacypolicy/fi/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="en">https://corp.example.org/privacypolicy/en/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="sv">https://corp.example.org/privacypolicy/sv/</mdui:PrivacyStatementURL>
      </mdui:UIInfo>
    </Extensions>
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
    <AttributeConsumingService index="1">
      <ServiceName xml:lang="fi">Mun ohjelma</ServiceName>
      <ServiceName xml:lang="en">My program name</ServiceName>
      <ServiceName xml:lang="sv">Mitt program</ServiceName>
      <ServiceDescription xml:lang="fi">Tämän palvelun testaus</ServiceDescription>
      <ServiceDescription xml:lang="en">Testing this service</ServiceDescription>
      <ServiceDescription xml:lang="sv">Testa denna tjänst</ServiceDescription>
    </AttributeConsumingService>
  </SPSSODescriptor>
  <Organization>
    <OrganizationName xml:lang="fi">Corp Oy</OrganizationName>
    <OrganizationName xml:lang="en">Corp Ltd</OrganizationName>
    <OrganizationName xml:lang="sv">Corp Ab</OrganizationName>
    <OrganizationDisplayName xml:lang="fi">Corporation Oy</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="en">Corporation Ltd</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="sv">Corporation Ab</OrganizationDisplayName>
    <OrganizationURL xml:lang="fi">https://corp.example.org/fi/</OrganizationURL>
    <OrganizationURL xml:lang="en">https://corp.example.org/en/</OrganizationURL>
    <OrganizationURL xml:lang="sv">https://corp.example.org/sv/</OrganizationURL>
  </Organization>
</EntityDescriptor>""")


@then(u'the page will have metadata 1')
def check_for_unvalidated_metadata(context):
    assert context.browser.is_text_present("""<EntityDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:mdattr="urn:oasis:names:tc:SAML:metadata:attribute" xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" entityID="https://sp.example.org/sp">
  <SPSSODescriptor AuthnRequestsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <Extensions>
      <idpdisc:DiscoveryResponse xmlns:idpdisc="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Location="https://discovery.example.org/" index="1"/>
      <init:RequestInitiator xmlns:init="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Binding="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Location="https://corp.example.org/login/"/>
      <mdui:UIInfo>
        <mdui:DisplayName xml:lang="fi">Mun ohjelma</mdui:DisplayName>
        <mdui:DisplayName xml:lang="en">My program name</mdui:DisplayName>
        <mdui:DisplayName xml:lang="sv">Mitt program</mdui:DisplayName>
        <mdui:Description xml:lang="fi">Tämän palvelun testaus</mdui:Description>
        <mdui:Description xml:lang="en">Testing this service</mdui:Description>
        <mdui:Description xml:lang="sv">Testa denna tjänst</mdui:Description>
        <mdui:PrivacyStatementURL xml:lang="fi">https://corp.example.org/privacypolicy/fi/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="en">https://corp.example.org/privacypolicy/en/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="sv">https://corp.example.org/privacypolicy/sv/</mdui:PrivacyStatementURL>
      </mdui:UIInfo>
    </Extensions>
    <KeyDescriptor>
      <ds:KeyInfo>
        <ds:X509Data>
          <ds:X509Certificate>MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
BAMMDnNwLmV4YW1wbGUub3JnMB4XDTE4MDExNjExMTAxN1oXDTI4MDExNDExMTAx
N1owGTEXMBUGA1UEAwwOc3AuZXhhbXBsZS5vcmcwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDlomqiyCbu1nKL9BtTwFjuNr0O2iDrQ1DbOnMu6E3tg0CO
kvmxzy7e9RuVzJUzz4bCz5u7xoHAFzaOX/k0FwRp32k9//4KNiioZta+sOE5ewyi
9ooOxqYtBMC7xy4AF/+7U2XoeGvdPPswUjEB0b312K4Xu3tvQy4ZdDhIiIHizLng
bHOUX8Isq50z8PmSEPE/DMMfK4mvfSMT067fC6tX+WHjlb8PHgEBn09f8kL76+x6
JLm6uGPN2M0lL1mtoN3lumYxldifsf2REuZdVSQYGRqQWjvMDJCPy1NRyvUHRDRr
FWIgEJhSpp0PdLd+9oK4Wccw8L2PN/khpXAJAVrAuMrOzASWL+ZuCQbUHSoK0Asb
4eN5jgDBNU63P/Ev4//JaUwNmYWMSeqEEKzun0WansZFC2LUkVjvuSZ2JV4bzu+s
pRdj0dkEa5HOhk7Bvd/eN0h2aVLsF3EgXekDudbKXMwQOxrazJoVHv9pwxsZxlHK
LP298175K/skR8VASQdH3JBrXpdiDb4mLoyXdx/I11Tx13fuiQogIRcm6ccqy/Ob
1nFzh1tkqTaFJF2F3cLCpbrqv853vWC08bRACkIeJQ8R8EDJudvk3cQllHHfItss
yoR//TcHJXsu+zwTruW6wdLkXShG3v2N2zplChuUczFYOT1FjZa+hRhk8p6tOwID
AQABo1AwTjAdBgNVHQ4EFgQU2TjrYXoZH0JkPA3YIZe+H0v1jqcwHwYDVR0jBBgw
FoAU2TjrYXoZH0JkPA3YIZe+H0v1jqcwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0B
AQsFAAOCAgEAJUjWKsLdtVI5xqfi7RLk1viyTdvKi2sTkXgKySNPffwRLoEcmIAp
FPX0TAhsoBdxE7OFwlSmb6ZX89CtNlwyyVHlWemwgKNfjdgj0qkk7Lreq+L1si6j
diml6uFfMbZrHtppxHENDYckxxfD3Zooa/pY9NUG17BHzoNTAsDhFq7YCA4Y2j6h
acYh1pa0PQ4rhE2zhFs3AZF+gaYGdwtKEcJBEQ6OcctP3Y8K/FTDmJAK3dERdmrh
BdeYSRTQSQMm0W1SsIsEMEfndC1Cca/aKrl8B1tZz55s04WPx/e92NV9S5KGRH0G
UADycvLo12NUfqubK+2+bcH92rhHZ1QGjkfJmHwhXIqt8F1gysQQO+M3uYhlpiIR
4vQBWFqoMCT7lqQYj1tCvrt6+RVv3Zz8t0eMfJXSFAoJPbjv3npPcUfjmLRG7W9y
VSb6gzk3PYRVB0NzmlPdB4KFdBQbsuE8qoPr3UBbHIiD9wFU6K6eUZkIjqIV/5az
56c2mntFDpdx+46RkS/7CEAbZkD8kEM5vrhpDXhbfLzIDTnOTBTbrwGmPCnpYSXy
rKLt+NcwtbkI6weLISJu9lFZnPMYT7LpqDWD4aMHHUWr8THO0T6mbCeQRYMlfSpU
0es8zIhYt2fRbxHFRIFyRZYJrQoSfkU5OMas/ypz/q2wOvgqjH8qyRQ=
</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://sp.example.org/Shibboleth.sso/SAML2/POST"/>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://sp.example.org/Shibboleth.sso/SAML2/POST/2" ResponseLocation="https://sp.example.org/Shibboleth.sso/SAML2/POST/2Response" index="1" isDefault="true"/>
    <AttributeConsumingService index="1">
      <ServiceName xml:lang="fi">Mun ohjelma</ServiceName>
      <ServiceName xml:lang="en">My program name</ServiceName>
      <ServiceName xml:lang="sv">Mitt program</ServiceName>
      <ServiceDescription xml:lang="fi">Tämän palvelun testaus</ServiceDescription>
      <ServiceDescription xml:lang="en">Testing this service</ServiceDescription>
      <ServiceDescription xml:lang="sv">Testa denna tjänst</ServiceDescription>
      <RequestedAttribute FriendlyName="eduPersonScopedAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
      <RequestedAttribute FriendlyName="mail" Name="urn:oid:0.9.2342.19200300.100.1.3" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
      <RequestedAttribute FriendlyName="schacPersonalUniqueCode" Name="urn:oid:1.3.6.1.4.1.25178.1.2.14" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
    </AttributeConsumingService>
  </SPSSODescriptor>
  <ContactPerson contactType="technical">
    <GivenName>Tech</GivenName>
    <SurName>Boss</SurName>
    <EmailAddress>technical@example.org</EmailAddress>
  </ContactPerson>
  <ContactPerson contactType="administrative">
    <GivenName>Teppo</GivenName>
    <SurName>Testeri</SurName>
    <EmailAddress>tester@example.org</EmailAddress>
  </ContactPerson>
  <Organization>
    <OrganizationName xml:lang="fi">Corp Oy</OrganizationName>
    <OrganizationName xml:lang="en">Corp Ltd</OrganizationName>
    <OrganizationName xml:lang="sv">Corp Ab</OrganizationName>
    <OrganizationDisplayName xml:lang="fi">Corporation Oy</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="en">Corporation Ltd</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="sv">Corporation Ab</OrganizationDisplayName>
    <OrganizationURL xml:lang="fi">https://corp.example.org/fi/</OrganizationURL>
    <OrganizationURL xml:lang="en">https://corp.example.org/en/</OrganizationURL>
    <OrganizationURL xml:lang="sv">https://corp.example.org/sv/</OrganizationURL>
  </Organization>
</EntityDescriptor>""")


@then(u'the page will have metadata 2')
def check_for_validated_metadata(context):
    assert context.browser.is_text_present("""<EntityDescriptor xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:mdattr="urn:oasis:names:tc:SAML:metadata:attribute" xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" entityID="https://sp.example.org/sp">
  <Extensions>
    <mdattr:EntityAttributes>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/signResponses" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xsd:boolean">false</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/encryptAssertions" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xsd:boolean">false</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/saml2/sso/browser/encryptNameIDs" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue xsi:type="xsd:boolean">false</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/securityConfiguration" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue>shibboleth.SecurityConfiguration.SHA1</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/defaultAuthenticationMethods" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue>https://refeds.org/profile/mfa</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/disallowedFeatures" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue>0x1</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="http://shibboleth.net/ns/profiles/nameIDFormatPrecedence" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
        <saml:AttributeValue>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</saml:AttributeValue>
      </saml:Attribute>
    </mdattr:EntityAttributes>
  </Extensions>
  <SPSSODescriptor WantAssertionsSigned="true" AuthnRequestsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <Extensions>
      <idpdisc:DiscoveryResponse xmlns:idpdisc="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Binding="urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol" Location="https://discovery.example.org/" index="1"/>
      <init:RequestInitiator xmlns:init="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Binding="urn:oasis:names:tc:SAML:profiles:SSO:request-init" Location="https://corp.example.org/login/"/>
      <mdui:UIInfo>
        <mdui:DisplayName xml:lang="fi">Mun ohjelma</mdui:DisplayName>
        <mdui:DisplayName xml:lang="en">My program name</mdui:DisplayName>
        <mdui:DisplayName xml:lang="sv">Mitt program</mdui:DisplayName>
        <mdui:Description xml:lang="fi">Tämän palvelun testaus</mdui:Description>
        <mdui:Description xml:lang="en">Testing this service</mdui:Description>
        <mdui:Description xml:lang="sv">Testa denna tjänst</mdui:Description>
        <mdui:PrivacyStatementURL xml:lang="fi">https://corp.example.org/privacypolicy/fi/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="en">https://corp.example.org/privacypolicy/en/</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="sv">https://corp.example.org/privacypolicy/sv/</mdui:PrivacyStatementURL>
      </mdui:UIInfo>
    </Extensions>
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://sp.example.org/Shibboleth.sso/SAML2/POST"/>
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://sp.example.org/Shibboleth.sso/SAML2/POST/2" ResponseLocation="https://sp.example.org/Shibboleth.sso/SAML2/POST/2Response" index="1" isDefault="true"/>
    <AttributeConsumingService index="1">
      <ServiceName xml:lang="fi">Mun ohjelma</ServiceName>
      <ServiceName xml:lang="en">My program name</ServiceName>
      <ServiceName xml:lang="sv">Mitt program</ServiceName>
      <ServiceDescription xml:lang="fi">Tämän palvelun testaus</ServiceDescription>
      <ServiceDescription xml:lang="en">Testing this service</ServiceDescription>
      <ServiceDescription xml:lang="sv">Testa denna tjänst</ServiceDescription>
      <RequestedAttribute FriendlyName="eduPersonScopedAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
      <RequestedAttribute FriendlyName="mail" Name="urn:oid:0.9.2342.19200300.100.1.3" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
    </AttributeConsumingService>
  </SPSSODescriptor>
  <ContactPerson contactType="technical">
    <GivenName>Tech</GivenName>
    <SurName>Boss</SurName>
    <EmailAddress>technical@example.org</EmailAddress>
  </ContactPerson>
  <ContactPerson contactType="administrative">
    <GivenName>Teppo</GivenName>
    <SurName>Testeri</SurName>
    <EmailAddress>tester@example.org</EmailAddress>
  </ContactPerson>
  <Organization>
    <OrganizationName xml:lang="fi">Corp Oy</OrganizationName>
    <OrganizationName xml:lang="en">Corp Ltd</OrganizationName>
    <OrganizationName xml:lang="sv">Corp Ab</OrganizationName>
    <OrganizationDisplayName xml:lang="fi">Corporation Oy</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="en">Corporation Ltd</OrganizationDisplayName>
    <OrganizationDisplayName xml:lang="sv">Corporation Ab</OrganizationDisplayName>
    <OrganizationURL xml:lang="fi">https://corp.example.org/fi/</OrganizationURL>
    <OrganizationURL xml:lang="en">https://corp.example.org/en/</OrganizationURL>
    <OrganizationURL xml:lang="sv">https://corp.example.org/sv/</OrganizationURL>
  </Organization>
</EntityDescriptor>""")
