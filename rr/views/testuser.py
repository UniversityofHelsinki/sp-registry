from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.testuser import TestUser, TestUserData
from rr.forms.testuser import TestUserForm, TestUserDataForm
from rr.models.attribute import Attribute
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from random import randint
import logging

logger = logging.getLogger(__name__)


def generate_user_data(testuser, userdata=True, otherdata=True, scope="@example.org"):
    attributes = SPAttribute.objects.filter(sp=testuser.sp, end_at=None)
    for attribute in attributes:
        if userdata:
            if attribute.attribute.friendlyname == "cn":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.firstname + " " + testuser.lastname})
            elif attribute.attribute.friendlyname == "givenName":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.firstname})
            elif attribute.attribute.friendlyname == "sn":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.lastname})
            elif attribute.attribute.friendlyname == "displayName":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.firstname + " " + testuser.lastname})
            elif attribute.attribute.friendlyname == "cn":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.firstname + " " + testuser.lastname})
            elif attribute.attribute.friendlyname == "uid":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.username})
            elif attribute.attribute.friendlyname == "mail":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.firstname.lower() + "." + testuser.lastname.lower() + scope})
            elif attribute.attribute.friendlyname == "eduPersonPrincipalName":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': testuser.username + scope})
        if otherdata:
            if attribute.attribute.friendlyname == "funetEduPersonStudentID":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': str(randint(100000, 999999))})
            if attribute.attribute.friendlyname == "employeeNumber":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': str(randint(100000, 999999))})
            if attribute.attribute.friendlyname == "eduPersonAffiliation":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "member;staff;employee;student"})
            if attribute.attribute.friendlyname == "eduPersonScopedAffiliation":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "member" + scope + ";staff" + scope + ";employee" + scope + ";student" + scope})
            if attribute.attribute.friendlyname == "eduPersonPrimaryAffiliation":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "employee"})
            if attribute.attribute.friendlyname == "preferredLanguage":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "fi"})
            if attribute.attribute.friendlyname == "schacDateOfBirth":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': str(randint(1960, 1998)) + "0213"})
            if attribute.attribute.friendlyname == "preferredLanguage":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "fi"})
            if attribute.attribute.friendlyname == "schacHomeOrganizationType":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "urn:schac:homeOrganizationType:fi:university"})
            if attribute.attribute.friendlyname == "schacCountryOfCitizenship":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "fi"})
            if attribute.attribute.friendlyname == "schacHomeOrganization":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "helsinki.fi"})
            if attribute.attribute.friendlyname == "schacGender":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "9"})
            if attribute.attribute.friendlyname == "mobile":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "0501234567"})
            if attribute.attribute.friendlyname == "schacMotherTongue":
                TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                                      defaults={'value': "fi"})


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

    ``form``
        ModelForm for creating a :model:`rr.TestUser`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/testuser.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404(_("Service provided does not exist"))
    form = TestUserForm(sp=sp)
    if request.method == "POST":
        if "add_testuser" in request.POST:
            form = TestUserForm(request.POST, sp=sp)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                userdata = form.cleaned_data['userdata']
                otherdata = form.cleaned_data['otherdata']
                testuser = TestUser.objects.create(sp=sp, username=username, password=password, firstname=firstname, lastname=lastname, end_at=None)
                logger.info("Test user {username} added for {sp}".format(username=username, sp=sp))
                form = TestUserForm(sp=sp)
                generate_user_data(testuser, userdata, otherdata)
        elif "remove_testuser" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    testuser = TestUser.objects.get(pk=key)
                    if testuser.sp == sp:
                        testuser.end_at = timezone.now()
                        testuser.save()
                        logger.info("Test user {username} removed from {sp}".format(username=testuser.username, sp=sp))
    testusers = TestUser.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/testuser.html", {'object_list': testusers,
                                                'form': form,
                                                'object': sp})


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
    if not request.user.is_superuser and not ServiceProvider.objects.get(pk=testuser.pk, admins=request.user, end_at=None):
        raise Http404(_("User provided does not exist"))
    if request.method == "POST":
        if "save_data" in request.POST:
            form = TestUserDataForm(request.POST, user=testuser)
            if form.is_valid():
                for field in form:
                    data = form.cleaned_data.get(field.name)
                    userdata = TestUserData.objects.filter(user=testuser, attribute__friendlyname=field.name).first()
                    if userdata and not data:
                        userdata.delete()
                    elif data:
                        if not userdata:
                            attribute = Attribute.objects.filter(friendlyname=field.name).first()
                            TestUserData.objects.create(user=testuser,
                                                        attribute=attribute,
                                                        value=data)
                        else:
                            if userdata.value != data:
                                userdata.value = data
                                userdata.save()
        if "reset_userdata" in request.POST:
            generate_user_data(testuser, userdata=True, otherdata=False)
            form = TestUserDataForm(user=testuser)
        if "reset_otherdata" in request.POST:
            generate_user_data(testuser, userdata=False, otherdata=True)
            form = TestUserDataForm(user=testuser)
    else:
        form = TestUserDataForm(user=testuser)
    return render(request, "rr/testuser_attribute_data.html", {'form': form,
                                                               'object': testuser.sp,
                                                               'testuser': testuser})
