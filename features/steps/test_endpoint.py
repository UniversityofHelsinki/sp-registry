from behave import when, then, given


@when(u'filling endpoint form with location "{location}"')
def fill_endpoint(context, location):
    context.browser.fill("location", location)
    context.browser.select("type", "AssertionConsumerService")
    context.browser.select("binding", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")
    context.browser.find_by_text('Save').first.click()


@when(u'filling endpoint form with location and response "{location}"')
def fill_endpoint_with_response_location(context, location):
    context.browser.fill("location", location)
    context.browser.fill("response_location", location + 'Response')
    context.browser.fill("index", "1")
    context.browser.check("is_default")
    context.browser.select("type", "AssertionConsumerService")
    context.browser.select("binding", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")
    context.browser.find_by_text('Save').first.click()


@when(u'removing first endpoint')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_endpoint').first.click()
    context.browser.find_by_text('Confirm').first.click()
