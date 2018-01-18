from behave import when, then, given
from django.core.management import call_command
from django.utils.six import StringIO


@when(u'loading test metadata')
def load_test_metadata(context):
    out = StringIO()
    call_command('importmetadata', 'testdata/metadata.xml', stdout=out)


@then(u'the page will have same metadata')
def check_for_text(context):
    assert context.browser.is_text_present("""<EntityDescriptor entityID="https://sp.example.org/sp" schemaLocation="urn:oasis:names:tc:SAML:2.0:metadata">
  <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <Extensions>
      <mdui:UIInfo xmlns:mdui="urn:oasis:names:tc:SAML:metadata:ui">
        <mdui:DisplayName xml:lang="fi">Testiohjelma</mdui:DisplayName>
        <mdui:DisplayName xml:lang="en">Test application</mdui:DisplayName>
        <mdui:DisplayName xml:lang="sv">Testapplikation</mdui:DisplayName>
        <mdui:Description xml:lang="fi">Testimetadata resurssirekisteriin</mdui:Description>
        <mdui:Description xml:lang="en">Testing metadata for resource registry</mdui:Description>
        <mdui:Description xml:lang="sv">Testa metadata f&#246;r resursregistret</mdui:Description>
        <mdui:PrivacyStatementURL xml:lang="fi">https://sp.example.org/privacy/policy_fi.pdf</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="en">https://sp.example.org/privacy/policy_en.pdf</mdui:PrivacyStatementURL>
        <mdui:PrivacyStatementURL xml:lang="sv">https://sp.example.org/privacy/policy_ev.pdf</mdui:PrivacyStatementURL>
      </mdui:UIInfo>
    </Extensions>
    <KeyDescriptor xmlns:ds="urn:oasis:names:tc:SAML:2.0:metadata">
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
      <ServiceDescription xml:lang="sv">Testa metadata f&#246;r resursregistret</ServiceDescription>
      <RequestedAttribute FriendlyName="funetEduPersonStudentID" Name="urn:oid:1.3.6.1.4.1.16161.1.1.10" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
      <RequestedAttribute FriendlyName="mail" Name="urn:oid:0.9.2342.19200300.100.1.3" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"/>
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
