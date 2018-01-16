from behave import when, then, given


@when(u'filling endpoint form with url "{url}"')
def fill_endpoint(context, url):
    context.browser.fill("url", url)
    context.browser.fill("index", "1")
    context.browser.select("type", "AssertionConsumerService")
    context.browser.select("binding", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")
    context.browser.find_by_text('Submit').first.click()


@when(u'removing first endpoint')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_endpoint').first.click()
