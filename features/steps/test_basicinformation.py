from behave import when, then, given


@when(u'filling basic information form with invalid information')
def fill_basic_form_invalid(context):
    context.browser.fill("name_en", "My new program name")
    context.browser.fill("entity_id", "invalid_entity_id")
    context.browser.fill("privacypolicy_en", "https://privacy.example.org/sp.pdf")
    context.browser.find_by_text('Save').first.click()


@when(u'filling basic information form')
def fill_basic_form(context):
    context.browser.fill("name_en", "My new program name")
    context.browser.fill("entity_id", "https://sp.example.org/sp")
    context.browser.fill("privacypolicy_en", "https://privacy.example.org/sp.pdf")
    context.browser.find_by_text('Save').first.click()


@when(u'setting publish to test servers')
def publish_to_prodcution_Server(context):
    context.browser.check("test")
    context.browser.find_by_text('Save').first.click()
