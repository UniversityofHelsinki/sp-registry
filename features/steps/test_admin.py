from behave import when, then, given
from django.core import mail


@when(u'filling invite form with email "{email}"')
def fill_endpoint(context, email):
    context.browser.fill("email", email)
    context.browser.find_by_text('Send invitation').first.click()


@when(u'removing admin')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_admin').first.click()


@when(u'removing admin invite')
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_invite').first.click()


@then('there should be invitation in email')
def impl(context):
    assert "Teemu Testeri has added you" in mail.outbox[0].body
