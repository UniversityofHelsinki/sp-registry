from behave import when, then, given


@when(u'filling email form')
def filling_email_form(context):
    context.browser.check("service_type")
    context.browser.check("test_sp")
    context.browser.check("admin_emails")
    context.browser.select("template", "1")
    context.browser.find_by_name('show_message').first.click()


@when(u'sending email form')
def sending_email_form(context):
    context.browser.find_by_name('send_email').first.click()
