from rr.models.serviceprovider import SPAttribute
from rr.models.testuser import TestUserData

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