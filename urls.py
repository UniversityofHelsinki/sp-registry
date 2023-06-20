from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from auth.views.authtoken import authtoken
from rr.routers import router
from rr.views.attribute import attribute_admin_list, attribute_list, attribute_view
from rr.views.certificate import (
    certificate_admin_list,
    certificate_info,
    certificate_list,
)
from rr.views.contact import contact_list
from rr.views.email import email_list
from rr.views.endpoint import endpoint_list
from rr.views.login import ShibbolethLoginView, logout_redirect
from rr.views.metadata import metadata, metadata_import, metadata_management
from rr.views.redirecturi import redirecturi_list
from rr.views.serviceprovider import (
    BasicInformationUpdate,
    BasicInformationView,
    LdapServiceProviderCreate,
    LdapTechnicalInformationUpdate,
    OidcServiceProviderCreate,
    OidcTechnicalInformationUpdate,
    SAMLAdminList,
    SamlServiceProviderCreate,
    SamlTechnicalInformationUpdate,
    ServiceProviderDelete,
    ServiceProviderList,
)
from rr.views.sp_errors import sp_error
from rr.views.spadmin import activate_key, admin_list
from rr.views.statistics import statistics_list, statistics_summary_list
from rr.views.testuser import testuser_attribute_data, testuser_list
from rr.views.usergroup import usergroup_list

schema_view = get_schema_view(
    openapi.Info(
        title="SP Registry API",
        default_version="1.0",
        description="REST API for modifying service provider information.",
        contact=openapi.Contact(name="Technical contact", email=settings.DEFAULT_CONTACT_EMAIL),
    )
)

# Overwrite default status handlers
handler400 = "rr.views.handlers.bad_request"
handler403 = "rr.views.handlers.permission_denied"
handler404 = "rr.views.handlers.page_not_found"
handler500 = "rr.views.handlers.server_error"

urlpatterns = [
    path("api/v1/", include(router.urls)),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    url(r"^admin_django/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin_django/", admin.site.urls),
    url(r"^$", login_required(ServiceProviderList.as_view()), name="front-page"),
    url(r"^authtoken/$", authtoken, name="auth-token"),
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(r"^login/shibboleth/$", ShibbolethLoginView.as_view(), name="shibboleth-login"),
    url(r"^logout/$", logout_redirect, name="logout"),
    url(
        r"^logout/local/$",
        LogoutView.as_view(template_name="registration/logout.html", redirect_field_name="return"),
        name="logout-local",
    ),
    url(r"^list/$", login_required(ServiceProviderList.as_view()), name="serviceprovider-list"),
    url(r"^admin/(?P<pk>[0-9]+)/$", admin_list, name="admin-list"),
    url(r"^attribute/(?P<pk>[0-9]+)/$", attribute_list, name="attribute-list"),
    url(r"^attribute/list/$", attribute_admin_list, name="attribute-admin-list"),
    url(r"^attribute/view/(?P<pk>[0-9]+)/$", attribute_view, name="attribute-view"),
    url(r"^certificate/(?P<pk>[0-9]+)/$", certificate_list, name="certificate-list"),
    url(r"^certificate/info/(?P<pk>[0-9]+)/$", certificate_info, name="certificate-info"),
    url(r"^certificate/list/$", certificate_admin_list, name="certificate-admin-list"),
    url(r"^contact/(?P<pk>[0-9]+)/$", contact_list, name="contact-list"),
    url(r"^endpoint/(?P<pk>[0-9]+)/$", endpoint_list, name="endpoint-list"),
    url(r"^email/$", email_list, name="email-list"),
    url(r"^metadata/import/$", metadata_import, name="metadata-import"),
    url(r"^metadata/manage/saml/$", metadata_management, {"service_type": "saml"}, name="metadata-manage-saml"),
    url(r"^metadata/manage/ldap/$", metadata_management, {"service_type": "ldap"}, name="metadata-manage-ldap"),
    url(r"^metadata/manage/oidc/$", metadata_management, {"service_type": "oidc"}, name="metadata-manage-oidc"),
    url(r"^metadata/(?P<pk>[0-9]+)/$", metadata, name="metadata-view"),
    url(r"^redirecturi/(?P<pk>[0-9]+)/$", redirecturi_list, name="redirecturi-list"),
    url(
        r"^technical/(?P<pk>[0-9]+)/$",
        login_required(SamlTechnicalInformationUpdate.as_view()),
        name="technical-update",
    ),
    url(
        r"^ldap/(?P<pk>[0-9]+)/$",
        login_required(LdapTechnicalInformationUpdate.as_view()),
        name="ldap-technical-update",
    ),
    url(
        r"^oidc/(?P<pk>[0-9]+)/$",
        login_required(OidcTechnicalInformationUpdate.as_view()),
        name="oidc-technical-update",
    ),
    url(
        r"^serviceprovider/add/saml/$",
        login_required(SamlServiceProviderCreate.as_view()),
        name="saml-serviceprovider-add",
    ),
    url(
        r"^serviceprovider/add/ldap/$",
        login_required(LdapServiceProviderCreate.as_view()),
        name="ldap-serviceprovider-add",
    ),
    url(
        r"^serviceprovider/add/oidc/$",
        login_required(OidcServiceProviderCreate.as_view()),
        name="oidc-serviceprovider-add",
    ),
    url(
        r"^serviceprovider/remove/(?P<pk>[0-9]+)/$",
        login_required(ServiceProviderDelete.as_view()),
        name="serviceprovider-delete",
    ),
    url(
        r"^serviceprovider/(?P<pk>[0-9]+)/$",
        login_required(BasicInformationUpdate.as_view()),
        name="basicinformation-update",
    ),
    url(r"^saml_admin_list/$", login_required(SAMLAdminList.as_view()), name="saml-admin-list"),
    url(r"^statistics/summary/$", statistics_summary_list, name="statistics-summary-list"),
    url(r"^statistics/(?P<pk>[0-9]+)/$", statistics_list, name="statistics-list"),
    url(r"^summary/(?P<pk>[0-9]+)/$", login_required(BasicInformationView.as_view()), name="summary-view"),
    url(r"^testuser/(?P<pk>[0-9]+)/$", testuser_list, name="testuser-list"),
    url(r"^testuser/data/(?P<pk>[0-9]+)/$", testuser_attribute_data, name="testuser-attribute-data"),
    url(r"^usergroup/(?P<pk>[0-9]+)/$", usergroup_list, name="usergroup-list"),
    url(r"^invite/$", activate_key, name="invite-activate"),
    url(r"^invite/(?P<invite_key>[\w+\s-]+)/$", activate_key, name="invite-activate-key"),
    url(r"^error/$", sp_error, name="error"),
    url("^", include("django.contrib.auth.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
]
