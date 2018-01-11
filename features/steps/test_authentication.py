from behave import when, then


@when('I visit the "{url}"')
def impl(context, url):
    context.response = context.test.client.get(url, follow=True)


@then('the result page will include "{text}"')
def visit(context, text):
    response = context.response
    context.test.assertContains(response, text)
