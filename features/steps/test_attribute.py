from behave import when, then, given


@when(u'filling attribute form')
def fill_basic_form_invalid(context):
    context.browser.fill("funetEduPersonStudentID", "Need this for authentication")
    context.browser.fill("mail", "Basic contact address")
    context.browser.find_by_text('Submit').first.click()


@when(u'removing attribute reason')
def fill_basic_form(context):
    context.browser.fill("funetEduPersonStudentID", "")
    context.browser.find_by_text('Submit').first.click()
