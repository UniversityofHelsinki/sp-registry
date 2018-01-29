from behave import when, then, given


@when(u'filling contact form with email "{email}"')
def fill_endpoint(context, email):
    context.browser.fill("email", email)
    context.browser.select("type", "administrative")
    context.browser.fill("firstname", "Teppo")
    context.browser.fill("lastname", "Testeri")
    context.browser.find_by_text('Save').first.click()


@when(u'removing first contact')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_contact').first.click()
    context.browser.find_by_text('Confirm').first.click()
