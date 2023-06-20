from behave import then, when
from django.core import mail

from rr.models.serviceprovider import ServiceProvider


@when('I visit the "{url}"')
def iumpl(context, url):
    context.browser.visit(context.base_url + url)


@when('clicking link with text "{text}"')
def click_link(context, text):
    context.browser.find_by_text(text).click()


@when('clicking visible link with text "{text}"')
def click_visible_link(context, text):
    elements = context.browser.find_by_text(text)
    for element in elements:
        if element.visible:
            element.click()
            break


@when('clicking object with text "{text}"')
def click_object_by_text(context, text):
    context.browser.find_by_text(text).first.click()


@when('clicking object with name "{text}"')
def click_object_by_name(context, text):
    context.browser.find_by_name(text).first.click()


@when('clicking object with value "{text}"')
def click_object_by_value(context, text):
    context.browser.find_by_value(text).first.click()


@then('the result page will include text "{text}"')
def check_for_text(context, text):
    assert context.browser.is_text_present(text)


@then('the result page will not include text "{text}"')
def check_for_missing_text(context, text):
    assert not context.browser.is_text_present(text)


@then('the page will include form value "{text}"')
def check_for_form_value(context, text):
    assert context.browser.find_by_value(text)


@then('the page will not include form value "{text}"')
def check_for_form_value_negation(context, text):
    assert not context.browser.find_by_value(text)


@then('count of tag "{text}" is "{number}"')
def count_id(context, text, number):
    assert len(context.browser.find_by_tag(text)) == int(number)


@then('the result page code include text "{text}"')
def check_for_code_text(context, text):
    assert text in context.browser.html


@then('logout"')
def logout(context):
    context.browser.find_by_text("Logout").first.click()


@then('message "{number}" in mailbox should have "{text}" in subject')
def check_mail_subject(context, number, text):
    message_number = int(number)
    assert text in mail.outbox[message_number].subject


@then('message "{number}" in mailbox should not have "{text}" in subject')
def check_mail_subject_negative(context, number, text):
    message_number = int(number)
    assert text not in mail.outbox[message_number].subject


@then('message "{number}" in mailbox should have "{text}" in body')
def check_mail_body(context, number, text):
    message_number = int(number)
    assert text in mail.outbox[message_number].body


@then('number of service providers is "{number}" and number of deleted is "{end_at}"')
def number_of_service_providers(context, number, end_at):
    providers = ServiceProvider.objects.filter(end_at=None).count()
    deleted = ServiceProvider.objects.filter(end_at__isnull=False).count()
    print(providers)
    print(deleted)
    assert int(number) == providers
    assert int(end_at) == deleted


@then('mailbox size should be "{number}"')
def check_mail_size(context, number):
    size = int(number)
    assert len(mail.outbox) == size


@when("empty mailbox")
def empty_mailbox(context):
    mail.outbox = []


@when('fill "{field}" with "{text}"')
def fill_field_with_text(context, field, text):
    context.browser.fill(field, text)


@when('checking "{checkbox}"')
def check_checkbox(context, checkbox):
    context.browser.check(checkbox)
