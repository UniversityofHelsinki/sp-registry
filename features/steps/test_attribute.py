from behave import when, then, given


@when(u'filling attribute form')
def fill_attribute_form(context):
    context.browser.fill("schacPersonalUniqueCode", "Need this for authentication")
    context.browser.fill("eduPersonScopedAffiliation", "Used for checking permissions")
    context.browser.fill("mail", "Basic contact address")
    context.browser.find_by_text('Save').first.click()


@when(u'removing attribute reason')
def remove_attribute_reason(context):
    context.browser.fill("schacPersonalUniqueCode", "")
    context.browser.find_by_text('Save').first.click()
