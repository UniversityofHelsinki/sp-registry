from django.contrib import admin
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.attribute import Attribute

admin.site.register(ServiceProvider)
admin.site.register(Attribute)
admin.site.register(SPAttribute)
