from behave import when, then, given


@when(u'filling test user form')
def fill_testuser(context):
    context.browser.fill("username", "shholmes")
    context.browser.fill("password", "mysecretpassword")
    context.browser.fill("firstname", "Sherlock")
    context.browser.fill("lastname", "Holmes")
    context.browser.check("userdata")
    context.browser.check("otherdata")
    valid_for = context.browser.find_by_id('id_valid_for')
    valid_for.select('3')
    context.browser.find_by_text('Save').first.click()


@when(u'removing external test user')
def remove_external_testuser(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_testuser_external').first.click()
    context.browser.find_by_text('Confirm').first.click()
