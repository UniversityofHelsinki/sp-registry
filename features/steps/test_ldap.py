from behave import when, then, given

@when(u'filling ldap technical information form with invalid information')
def fill_techical_form_invalid(context):
    context.browser.fill("server_names", "server+name")
    context.browser.find_by_text('Save').first.click()


@when(u'filling ldap technical information form')
def fill_technical_form(context):
    context.browser.fill("server_names", "ldap-modified.example.org")
    context.browser.find_by_text('Save').first.click()


@when(u'filling ldap creation form')
def fill_creation_form(context):
    context.browser.fill("server_names", "new.example.org")
    context.browser.fill("name_fi", "My new test service")
    context.browser.fill("description_fi", "New test service for testing this service")
    context.browser.fill("privacypolicy_en", "https://privacy.example.org/sp.pdf")
    context.browser.find_by_text('Save').first.click()
