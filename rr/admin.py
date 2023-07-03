from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rr.models.attribute import Attribute
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.email import Template
from rr.models.endpoint import Endpoint
from rr.models.nameidformat import NameIDFormat
from rr.models.oidc import GrantType, OIDCScope, ResponseType
from rr.models.organization import Organization
from rr.models.redirecturi import RedirectUri
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.spadmin import Keystore
from rr.models.statistics import Statistics
from rr.models.testuser import TestUser, TestUserData
from rr.models.usergroup import UserGroup


class DeletedFilter(admin.SimpleListFilter):
    title = _("Deleted")

    parameter_name = "end_at"

    def lookups(self, request, model_admin):
        return (
            (None, _("Active")),
            ("deleted", _("Deleted")),
            ("all", _("All")),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string(
                    {
                        self.parameter_name: lookup,
                    },
                    [],
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "all":
            return queryset
        elif self.value() == "deleted":
            return queryset.filter(end_at__isnull=False)
        else:
            if queryset.model.__name__ == "ServiceProvider":
                return queryset.filter(end_at__isnull=True)
            else:
                # Restrict listed values to active SPs
                return queryset.filter(end_at__isnull=True, sp__end_at__isnull=True)


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ["entity_id", "name", "service_type", "production", "test", "history"]
    list_filter = [DeletedFilter, "service_type", "production", "test"]
    search_fields = [
        "entity_id",
        "name_fi",
        "name_en",
        "name_sv",
        "service_type",
        "production",
        "test",
        "history",
        "admins__username",
        "admin_groups__name",
    ]
    autocomplete_fields = ["admins", "admin_groups"]


admin.site.register(ServiceProvider, ServiceProviderAdmin)


class AttributeAdmin(admin.ModelAdmin):
    list_display = ["friendlyname", "name", "public_saml", "public_ldap", "public_oidc"]
    list_filter = ["public_saml", "public_ldap", "public_oidc", "test_service"]
    search_fields = ["friendlyname", "name", "info"]
    autocomplete_fields = []


admin.site.register(Attribute, AttributeAdmin)


class SPAttributeAdmin(admin.ModelAdmin):
    list_display = ["attribute", "sp"]
    list_filter = [DeletedFilter]
    search_fields = ["attribute__friendlyname", "sp__entity_id"]
    autocomplete_fields = ["attribute", "sp"]


admin.site.register(SPAttribute, SPAttributeAdmin)


class CertificateAdmin(admin.ModelAdmin):
    list_display = ["cn", "valid_until", "key_size", "sp"]
    list_filter = [DeletedFilter, "signing", "encryption", "key_size"]
    search_fields = ["cn", "sp__entity_id"]


admin.site.register(Certificate, CertificateAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ["type", "firstname", "lastname", "email", "sp"]
    list_filter = [DeletedFilter, "type"]
    search_fields = ["firstname", "lastname", "email", "sp__entity_id"]


admin.site.register(Contact, ContactAdmin)


class EndpointAdmin(admin.ModelAdmin):
    list_display = ["type", "binding", "location", "sp"]
    list_filter = [DeletedFilter, "type", "binding"]
    search_fields = ["type", "binding", "location", "sp__entity_id"]


admin.site.register(Endpoint, EndpointAdmin)


admin.site.register(GrantType)


class KeystoreAdmin(admin.ModelAdmin):
    list_display = ["sp", "email", "valid_until", "creator"]
    search_fields = ["sp__entity_id", "email", "creator__username"]


admin.site.register(Keystore, KeystoreAdmin)


admin.site.register(NameIDFormat)
admin.site.register(OIDCScope)
admin.site.register(Organization)


class RedirectUriAdmin(admin.ModelAdmin):
    list_display = ["uri", "sp"]
    list_filter = [DeletedFilter]
    search_fields = ["uri", "sp__entity_id"]


admin.site.register(RedirectUri, RedirectUriAdmin)


admin.site.register(ResponseType)
admin.site.register(Statistics)
admin.site.register(Template)


class TestUserAdmin(admin.ModelAdmin):
    list_display = ["username", "sp"]
    list_filter = [DeletedFilter]
    search_fields = ["username", "sp__entity_id", "valid_for__entity_id"]


admin.site.register(TestUser, TestUserAdmin)


class TestUserDataAdmin(admin.ModelAdmin):
    list_display = ["user", "attribute"]
    list_filter = []
    search_fields = ["attribute__friendlyname", "user__username", "value"]


admin.site.register(TestUserData, TestUserDataAdmin)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ["sp", "name"]
    list_filter = [DeletedFilter]
    search_fields = ["name", "sp__entity_id"]


admin.site.register(UserGroup, UserGroupAdmin)
