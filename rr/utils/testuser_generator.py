from rr.models.serviceprovider import SPAttribute
from rr.models.testuser import TestUserData

from random import randint
import logging

logger = logging.getLogger(__name__)


def update_test_data(testuser, attribute, value):
    if TestUserData.objects.filter(user=testuser, attribute=attribute.attribute).count() < 2:
        TestUserData.objects.update_or_create(user=testuser, attribute=attribute.attribute,
                                              defaults={'value': value})


def generate_user_data(testuser, userdata=True, otherdata=True, scope="@example.org"):
    attributes = SPAttribute.objects.filter(sp=testuser.sp, end_at=None)
    for attribute in attributes:
        if userdata:
            if attribute.attribute.friendlyname == "cn":
                update_test_data(testuser, attribute, testuser.firstname + " " + testuser.lastname)
            elif attribute.attribute.friendlyname == "givenName":
                update_test_data(testuser, attribute, testuser.firstname)
            elif attribute.attribute.friendlyname == "sn":
                update_test_data(testuser, attribute, testuser.lastname)
            elif attribute.attribute.friendlyname == "displayName":
                update_test_data(testuser, attribute, testuser.firstname + " " + testuser.lastname)
            elif attribute.attribute.friendlyname == "cn":
                update_test_data(testuser, attribute, testuser.firstname + " " + testuser.lastname)
            elif attribute.attribute.friendlyname == "uid":
                update_test_data(testuser, attribute, testuser.username)
            elif attribute.attribute.friendlyname == "mail":
                update_test_data(testuser, attribute,
                                 testuser.firstname.lower() + "." + testuser.lastname.lower() + scope)
            elif attribute.attribute.friendlyname == "eduPersonPrincipalName":
                update_test_data(testuser, attribute, testuser.username + scope)
        if otherdata:
            if attribute.attribute.friendlyname == "funetEduPersonStudentID":
                update_test_data(testuser, attribute, str(randint(100000, 999999)))
            if attribute.attribute.friendlyname == "employeeNumber":
                update_test_data(testuser, attribute, str(randint(100000, 999999)))
            if attribute.attribute.friendlyname == "eduPersonAffiliation":
                update_test_data(testuser, attribute, "affiliate")
            if attribute.attribute.friendlyname == "eduPersonScopedAffiliation":
                update_test_data(testuser, attribute, "affiliate" + scope)
            if attribute.attribute.friendlyname == "eduPersonPrimaryAffiliation":
                update_test_data(testuser, attribute, "employee")
            if attribute.attribute.friendlyname == "preferredLanguage":
                update_test_data(testuser, attribute, "fi")
            if attribute.attribute.friendlyname == "schacDateOfBirth":
                update_test_data(testuser, attribute, str(randint(1960, 1998)) + "0213")
            if attribute.attribute.friendlyname == "preferredLanguage":
                update_test_data(testuser, attribute, "fi")
            if attribute.attribute.friendlyname == "schacHomeOrganizationType":
                update_test_data(testuser, attribute,
                                 "urn:schac:homeOrganizationType:fi:university")
            if attribute.attribute.friendlyname == "schacCountryOfCitizenship":
                update_test_data(testuser, attribute, "fi")
            if attribute.attribute.friendlyname == "schacHomeOrganization":
                update_test_data(testuser, attribute, "helsinki.fi")
            if attribute.attribute.friendlyname == "schacGender":
                update_test_data(testuser, attribute, "9")
            if attribute.attribute.friendlyname == "mobile":
                update_test_data(testuser, attribute, "0501234567")
            if attribute.attribute.friendlyname == "schacMotherTongue":
                update_test_data(testuser, attribute, "fi")
