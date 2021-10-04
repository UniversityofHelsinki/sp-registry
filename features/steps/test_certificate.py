from behave import when


@when(u'filling certificate form with invalid certificate')
def fill_invalid_certificate(context):
    certificate = """MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
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
0es8zIhYt2fRbxHFRIFyRZYJrQoSfkU5OMas/ypz/q2wOvgqjH8qyR
"""
    context.browser.fill("certificate", certificate)
    context.browser.check("encryption")
    context.browser.check("signing")
    context.browser.find_by_text('Save').first.click()


@when(u'filling certificate form with valid certificate')
def fill_valid_certificate(context):
    certificate = """MIIFBTCCAu2gAwIBAgIJAKOceIf3koqXMA0GCSqGSIb3DQEBCwUAMBkxFzAVBgNV
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
"""
    context.browser.fill("certificate", certificate)
    context.browser.check("encryption")
    context.browser.check("signing")
    context.browser.find_by_text('Save').first.click()


@when(u'removing first certificate')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_certificate').first.click()
    context.browser.find_by_text('Confirm').first.click()
