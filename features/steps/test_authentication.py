from behave import given, when
from django.contrib.auth.models import User

from rr.models.serviceprovider import ServiceProvider


@given('user "{username}" exists')
def create_user(context, username):
    u = User.objects.create_user(username=username, password="mysecretpassword")
    u.first_name = "Teemu"
    u.last_name = "Testeri"
    u.save()


@given('superuser "{username}" exists')
def create_superuser(context, username):
    u = User.objects.create_superuser(username=username, password="mysecretpassword", email="master.guy@example.org")
    u.first_name = "Master"
    u.last_name = "Guy"
    u.save()


@given('sp "{entity_id}" exists')
def create_sp(context, entity_id):
    ServiceProvider.objects.create(entity_id=entity_id, service_type="saml")


@given('user "{username}" is "{entity_id}" admin')
def add_admin(context, username, entity_id):
    u = User.objects.get(username=username)
    sp = ServiceProvider.objects.get(entity_id=entity_id)
    sp.admins.add(u)


@when('I login with "{username}" and "{password}"')
def login(context, username, password):
    context.browser.find_by_name("local_login").first.click()
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_text("Submit").first.click()
