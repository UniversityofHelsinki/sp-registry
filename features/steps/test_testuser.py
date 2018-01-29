from behave import when, then, given


@when(u'filling test user form')
def fill_testuser(context):
    context.browser.fill("username", "shholmes")
    context.browser.fill("password", "mysecretpassword")
    context.browser.fill("firstname", "Sherlock")
    context.browser.fill("lastname", "Holmes")
    context.browser.check("userdata")
    context.browser.check("otherdata")
    context.browser.find_by_text('Save').first.click()
