from behave import when, then, given

@when(u'filling ldap technical information form with invalid information')
def fill_techical_form_invalid(context):
    context.browser.fill("server_names", "server+name")
    context.browser.find_by_text('Save').first.click()


@when(u'filling ldap technical information form')
def fill_technical_form(context):
    context.browser.fill("server_names", "ldap.example.org ldap2.example.org")
    context.browser.find_by_text('Save').first.click()
