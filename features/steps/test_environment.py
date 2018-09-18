from behave import when, then, given

from django.contrib.auth.models import User
from django.utils import timezone

from rr.models.email import Template
from rr.models.serviceprovider import ServiceProvider
from rr.models.spadmin import Keystore


@given(u'test environment with logged in user exists')
def create_test_environment(context):
    username = "myself"
    password = "mysecretpassword"
    u = User.objects.create_user(username=username, password=password)
    u.first_name = "Teemu"
    u.last_name = "Testeri"
    u.email = "user@example.org"
    u.save()
    sp = ServiceProvider.objects.create(entity_id="https://sp.example.org/sp",
                                        name_en="My program name",
                                        validated=timezone.now(), modified=False)
    sp.admins.add(u)
    ServiceProvider.objects.create(entity_id="https://sp.example.com/sp",
                                   name_en="SP without admins",
                                   validated=timezone.now(), modified=False)
    sp = ServiceProvider.objects.create(entity_id="ldap-3", service_type="ldap",
                                        server_names="ldap.example.com ldap3.example.com",
                                        name_en="My LDAP service",
                                        validated=timezone.now(), modified=False)
    sp.admins.add(u)
    ServiceProvider.objects.create(entity_id="ldap-4", service_type="ldap",
                                   server_names="ldap.example.com ldap4.example.com",
                                   name_en="LDAP without admins",
                                   validated=timezone.now(), modified=False)
    context.browser.visit(context.base_url)
    context.browser.find_by_name('local_login').first.click()
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_text('Submit').first.click()


@given(u'test environment with LDAP service and logged in user exists')
def create_ldap_test_environment(context):
    username = "myself"
    password = "mysecretpassword"
    u = User.objects.create_user(username=username, password=password)
    u.first_name = "Teemu"
    u.last_name = "Testeri"
    u.save()
    sp = ServiceProvider.objects.create(entity_id="ldap-1", service_type="ldap",
                                        server_names="ldap.example.org", name_en="My program name",
                                        validated=timezone.now(), modified=False)
    sp.admins.add(u)
    ServiceProvider.objects.create(entity_id="ldap-2", service_type="ldap",
                                   server_names="ldap.example.com ldap2.example.com",
                                   name_en="SP without admins",
                                   validated=timezone.now(), modified=False)
    context.browser.visit(context.base_url)
    context.browser.find_by_name('local_login').first.click()
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_text('Submit').first.click()


@given(u'additional SP with admin exists')
def create_additional_SP(context):
    u = User.objects.all().first()
    sp = ServiceProvider.objects.create(entity_id="https://sp.example.net/sp",
                                        name_en="Additional SP",
                                        production=True, test=True,
                                        validated=timezone.now(), modified=False)
    sp.admins.add(u)


@given(u'test environment with logged in superuser exists')
def create_test_environment_with_superuser(context):
    username = "myself"
    password = "mysecretpassword"
    u = User.objects.create_superuser(username=username, email="superuser@example.org",
                                      password=password)
    u.first_name = "Teemu"
    u.last_name = "Testeri"
    u.save()
    sp = ServiceProvider.objects.create(entity_id="https://sp.example.org/sp",
                                        name_en="My program name", validated=timezone.now(),
                                        modified=False, test=True)
    sp.admins.add(u)
    ServiceProvider.objects.create(entity_id="https://sp.example.com/sp",
                                   name_en="SP without admins",
                                   validated=timezone.now(), modified=False)
    sp = ServiceProvider.objects.create(entity_id="ldap-3", service_type="ldap",
                                        server_names="ldap.example.com ldap3.example.com",
                                        name_en="My LDAP service",
                                        validated=timezone.now(), modified=False)
    sp.admins.add(u)
    ServiceProvider.objects.create(entity_id="ldap-4", service_type="ldap",
                                   server_names="ldap.example.com ldap4.example.com",
                                   name_en="LDAP without admins",
                                   validated=timezone.now(), modified=False)
    context.browser.visit(context.base_url)
    context.browser.find_by_name('local_login').first.click()
    context.browser.fill("username", username)
    context.browser.fill("password", password)
    context.browser.find_by_text('Submit').first.click()


@given(u'invite exists')
def create_invite(context):
    sp = ServiceProvider.objects.get(entity_id="https://sp.example.org/sp")
    user = User.objects.all().first()
    Keystore.objects.create(sp=sp,
                            creator=user,
                            activation_key="f5bc2a80eba67ca71df3dc740caf22a6eed7b2f3",
                            email="test@example.org",
                            valid_until=timezone.now())


@given(u'email template exists')
def create_email_template(context):
    Template.objects.create(title="Testing template", body="This is my message to SP admins.")
