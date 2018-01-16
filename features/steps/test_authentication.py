from behave import when, then, given
from django.contrib.auth.models import User
from rr.models.serviceprovider import ServiceProvider


@given(u'user "{username}" exists')
def create_user(context, username):
    u = User.objects.create_user(username=username, password='mysecretpassword')
    u.first_name = "Teemu"
    u.last_name = "Testeri"
    u.save()


@given(u'superuser "{username}" exists')
def create_superuser(context, username):
    u = User.objects.create_superuser(username=username, password='mysecretpassword', email="master.guy@example.org")
    u.first_name = "Master"
    u.last_name = "Guy"
    u.save()


@given(u'sp "{entity_id}" exists')
def create_sp(context, entity_id):
    ServiceProvider.objects.create(entity_id=entity_id)


@given(u'user "{username}" is "{entity_id}" admin')
def add_admin(context, username, entity_id):
    u = User.objects.get(username=username)
    sp = ServiceProvider.objects.get(entity_id=entity_id)
    sp.admins.add(u)


@when(u'I login with "{username}" and "{password}"')
def login(context, username, password):
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_text('Submit').first.click()
