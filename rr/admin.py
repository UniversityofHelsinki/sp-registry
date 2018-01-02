from django.contrib import admin
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.certificate import Certificate
from rr.models.attribute import Attribute
from rr.models.contact import Contact


admin.site.register(ServiceProvider)
admin.site.register(Attribute)
admin.site.register(SPAttribute)
admin.site.register(Certificate)
admin.site.register(Contact)
