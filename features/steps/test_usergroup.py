from behave import when


@when('filling user group form with name "{name}"')
def fill_usergroup(context, name):
    context.browser.fill("name", name)
    context.browser.find_by_text("Save").first.click()


@when("removing first user group")
def fill_basic_form(context):
    context.browser.check("1")
    context.browser.find_by_name("remove_usergroup").first.click()
    context.browser.find_by_text("Confirm").first.click()
