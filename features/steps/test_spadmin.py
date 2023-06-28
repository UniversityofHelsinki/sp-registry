from behave import when


@when('filling invite form with email "{email}"')
def fill_endpoint(context, email):
    context.browser.fill("email", email)
    context.browser.find_by_text("Send invitation").first.click()


@when('filling group form with name "{name}"')
def fill_endpoint(context, name):
    context.browser.fill("group", name)
    context.browser.find_by_text("Add group").first.click()


@when("removing admin")
def remove_admin(context):
    context.browser.find_by_id("id_admin").last.click()
    context.browser.find_by_text("Remove selected").first.click()
    context.browser.find_by_text("Confirm").first.click()


@when("removing admin invite")
def remove_invite(context):
    context.browser.find_by_id("id_invite").last.click()
    context.browser.find_by_text("Remove selected").last.click()
    context.browser.find_by_text("Confirm").last.click()


@when("removing admin group")
def remove_admin_group(context):
    context.browser.find_by_id("id_admin_group").last.click()
    context.browser.find_by_text("Remove selected").last.click()
    context.browser.find_by_text("Confirm").last.click()
