from behave import when, then, given


@when(u'I visit the "{url}"')
def iumpl(context, url):
    context.browser.visit(context.base_url + url)


@when(u'clicking link with text "{text}"')
def click_link(context, text):
    context.browser.click_link_by_text(text)


@when(u'clicking visible link with text "{text}"')
def click_visible_link(context, text):
    elements = context.browser.find_by_text(text)
    for element in elements:
        if element.visible:
            element.click()
            break


@then(u'the result page will include text "{text}"')
def check_for_text(context, text):
    assert context.browser.is_text_present(text)


@then(u'the result page will not include text "{text}"')
def check_for_missing_text(context, text):
    assert not context.browser.is_text_present(text)


@then(u'the page will include form value "{text}"')
def check_for_form_value(context, text):
    assert context.browser.find_by_value(text)


@then(u'count of tag "{text}" is "{number}"')
def count_id(context, text, number):
    assert len(context.browser.find_by_tag(text)) == int(number)


@then(u'the result page code include text "{text}"')
def check_for_code_text(context, text):
    assert text in context.browser.html


@then(u'logout"')
def logout(context):
    context.browser.find_by_text('Logout').first.click()
