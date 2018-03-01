from behave import when, then, given
from django.core import mail


@when(u'filling invite form with email "{email}"')
def fill_endpoint(context, email):
    context.browser.fill("email", email)
    context.browser.find_by_text('Send invitation').first.click()


@when(u'removing admin')
def remove_admin(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_admin').first.click()
    context.browser.find_by_text('Confirm').first.click()


@when(u'removing admin invite')
def remove_invite(context):
    context.browser.check("1")
    context.browser.find_by_name('remove_invite').first.click()
