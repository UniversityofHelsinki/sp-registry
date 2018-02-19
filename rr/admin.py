from django.contrib import admin
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.certificate import Certificate
from rr.models.attribute import Attribute
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.spadmin import Keystore
from rr.models.testuser import TestUser, TestUserData
from rr.models.organization import Organization
from rr.models.nameidformat import NameIDFormat


admin.site.register(ServiceProvider)
admin.site.register(Organization)
admin.site.register(Attribute)
admin.site.register(SPAttribute)
admin.site.register(Certificate)
admin.site.register(Contact)
admin.site.register(Endpoint)
admin.site.register(Keystore)
admin.site.register(NameIDFormat)
admin.site.register(TestUser)
admin.site.register(TestUserData)
