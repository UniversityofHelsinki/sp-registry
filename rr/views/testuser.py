import hashlib
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.forms.testuser import TestUserForm, TestUserDataForm, TestUserUpdateForm
from rr.utils.testuser_generator import generate_user_data
from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider
from rr.models.testuser import TestUser, TestUserData
from rr.utils.serviceprovider import get_service_provider

logger = logging.getLogger(__name__)


@login_required
def testuser_list(request, pk):
    """
    Displays a list of :model:`rr.TestUser` linked to
    :model:`rr.ServiceProvider`.

    Includes a ModelForm for adding :model:`rr.TestUser` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.TestUser`.

    ``object_list_external``
        List of :model:`rr.TestUser`.

    ``form``
        ModelForm for creating a :model:`rr.TestUser`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/testuser.html`
    """
    sp = get_service_provider(pk, request.user, service_type=["oidc", "saml"])
    form = TestUserForm(sp=sp, admin=request.user)
    if request.method == "POST":
        if "add_testuser" in request.POST:
            form = _add_testuser(request, sp)
        elif "remove_testuser" in request.POST:
            _remove_testusers(request, sp)
        elif "remove_testuser_external" in request.POST:
            _remove_external_testusers(request, sp)
    testusers = TestUser.objects.filter(sp=sp, end_at=None)
    testusers_external = TestUser.objects.filter(valid_for=sp).exclude(sp=sp)
    return render(request, "rr/testuser.html", {'object_list': testusers,
                                                'object_list_external': testusers_external,
                                                'form': form,
                                                'object': sp})


def _add_testuser(request, sp):
    form = TestUserForm(request.POST, sp=sp, admin=request.user)
    if form.is_valid():
        firstname = form.cleaned_data['firstname']
        lastname = form.cleaned_data['lastname']
        valid_for = form.cleaned_data['valid_for']
        userdata = form.cleaned_data['userdata']
        otherdata = form.cleaned_data['otherdata']
        scope = form.cleaned_data['scope'] if form.cleaned_data['scope'] else 'example.org'
        number_of_users = int(form.cleaned_data['number_of_users'])
        for number in range(1, number_of_users + 1):
            if number_of_users == 1:
                username = form.cleaned_data['username']
                password = hashlib.sha256(
                    form.cleaned_data['password'].encode('utf-8')).hexdigest()
            else:
                username = form.cleaned_data['username'] + str(number)
                password = hashlib.sha256(
                    (form.cleaned_data['password'] + str(number)).encode('utf-8')).hexdigest()
            if not TestUser.objects.filter(username=username, end_at=None).exists():
                testuser = TestUser.objects.create(sp=sp, username=username, password=password,
                                                   firstname=firstname, lastname=lastname,
                                                   end_at=None)

                testuser.valid_for.add(*valid_for)
                testuser.valid_for.add(sp)
                logger.info("Test user {username} added for {sp}"
                            .format(username=username, sp=sp))
                generate_user_data(testuser, userdata, otherdata, scope)
                messages.add_message(request, messages.INFO, _('Test user added: ') + username)
            else:
                messages.add_message(request, messages.WARNING, _('Username already exists: ') + username)
        form = TestUserForm(sp=sp, admin=request.user)
    return form


def _remove_testusers(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            testuser = TestUser.objects.get(pk=key)
            if testuser.sp == sp:
                testuser.end_at = timezone.now()
                testuser.save()
                logger.info("Test user {username} removed from {sp}"
                            .format(username=testuser.username, sp=sp))
                messages.add_message(request, messages.INFO,
                                     _('Test user removed: ') + testuser.username)


def _remove_external_testusers(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            testuser = TestUser.objects.get(pk=key)
            print(testuser)
            if sp in testuser.valid_for.all() and testuser.sp != sp:
                testuser.valid_for.remove(sp)
                logger.info("External test user {username} removed from {sp}"
                            .format(username=testuser.username, sp=sp))
                messages.add_message(request, messages.INFO,
                                     _('External test user removed: ') + testuser.username)


@login_required
def testuser_attribute_data(request, pk):
    """
    Displays a form including :model:`rr.Attribute` that
    are linked to :model:`rr.ServiceProvider` and values
    for

    If value is given, creates :model:`rr.TestUserData`

    If reason is removed, remove :model:`rr.TestUserData`

    **Context**

    ``form``
        List of :model:`rr.Attribute`.

    ``user_update_form``
        List of :model:`rr.TestUser`.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    ``testuser``
        An instance of :model:`rr.TestUser`.

    **Template:**

    :template:`rr/attribute_list.html`
    """
    try:
        testuser = TestUser.objects.get(pk=pk, end_at=None)
    except TestUser.DoesNotExist:
        raise Http404(_("User provided does not exist"))
    if not request.user.is_superuser and not ServiceProvider.objects.filter(pk=testuser.sp.pk,
                                                                            admins=request.user,
                                                                            end_at=None).first():
        raise Http404(_("User provided does not exist"))
    form = TestUserDataForm(user=testuser)
    user_update_form = TestUserUpdateForm(instance=testuser, sp=testuser.sp, admin=request.user)
    if request.method == "POST":
        if "save_data" in request.POST:
            form = _save_user_data(request, testuser)
        if "reset_userdata" in request.POST:
            generate_user_data(testuser, userdata=True, otherdata=False)
            form = TestUserDataForm(user=testuser)
            messages.add_message(request, messages.INFO,
                                 _('Name based data reset for test user: ') + testuser.username)
        if "reset_otherdata" in request.POST:
            generate_user_data(testuser, userdata=False, otherdata=True)
            form = TestUserDataForm(user=testuser)
            messages.add_message(request, messages.INFO,
                                 _('User data reset for test user: ') + testuser.username)
        if "update_user" in request.POST:
            user_update_form = _update_user(request, testuser)

    return render(request, "rr/testuser_attribute_data.html",
                  {'form': form,
                   'user_update_form': user_update_form,
                   'object': testuser.sp,
                   'testuser': testuser})


def _save_user_data(request, testuser):
    form = TestUserDataForm(request.POST, user=testuser)
    if form.is_valid():
        for field in form:
            data = form.cleaned_data.get(field.name)
            values = data.split(';')
            TestUserData.objects.filter(user=testuser,
                                        attribute__friendlyname=field.name).delete()
            for value in values:
                if value:
                    attribute = Attribute.objects.filter(friendlyname=field.name).first()
                    TestUserData.objects.create(user=testuser,
                                                attribute=attribute,
                                                value=value)
        messages.add_message(request, messages.INFO,
                             _('Test user attributes updated: ') + testuser.username)
    return form


def _update_user(request, testuser):
    temp_password = testuser.password
    user_update_form = TestUserUpdateForm(request.POST, instance=testuser, sp=testuser.sp,
                                          admin=request.user)
    if user_update_form.is_valid():
        testuser.firstname = user_update_form.cleaned_data['firstname']
        testuser.lastname = user_update_form.cleaned_data['lastname']
        testuser.valid_for.set(user_update_form.cleaned_data['valid_for'])
        password = user_update_form.cleaned_data['password']
        if password:
            testuser.password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        else:
            testuser.password = temp_password
        testuser.save()
        testuser.valid_for.add(testuser.sp)
        user_update_form = TestUserUpdateForm(instance=testuser, sp=testuser.sp,
                                              admin=request.user)
        messages.add_message(request, messages.INFO,
                             _('User info updated: ') + testuser.username)
    return user_update_form
