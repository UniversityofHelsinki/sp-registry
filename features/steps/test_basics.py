from behave import when, then, given
from django.contrib.auth.models import User
from rr.models.serviceprovider import ServiceProvider


@when(u'I visit the "{url}"')
def iumpl(context, url):
    context.browser.visit(context.base_url + url)


@when(u'clicking link with text "{text}"')
def click_link(context, text):
    context.browser.click_link_by_text(text)


@then(u'the result page will include text "{text}"')
def check_for_text(context, text):
    assert context.browser.is_text_present(text)


@then(u'the result page will not include text "{text}"')
def check_for_missing_text(context, text):
    assert not context.browser.is_text_present(text)


@then(u'count of tag "{text}" is "{number}"')
def count_id(context, text, number):
    assert len(context.browser.find_by_tag(text)) == int(number)


@then(u'the result page code include text "{text}"')
def check_for_code_text(context, text):
    assert text in context.browser.html
