from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

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
from rr.views.login import LocalLogoutView, ShibbolethLoginView
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

# Overwrite default status handlers
handler400 = "rr.views.handlers.bad_request"
handler403 = "rr.views.handlers.permission_denied"
handler404 = "rr.views.handlers.page_not_found"
handler500 = "rr.views.handlers.server_error"

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("swagger/", RedirectView.as_view(url="/api/schema/swagger/")),
    path("admin_django/doc/", include("django.contrib.admindocs.urls")),
    path("admin_django/", admin.site.urls),
    path("", login_required(ServiceProviderList.as_view()), name="front-page"),
    path("authtoken/", authtoken, name="auth-token"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/shibboleth/", ShibbolethLoginView.as_view(), name="shibboleth-login"),
    path("logout/", LocalLogoutView.as_view(), name="logout"),
    path("list/", login_required(ServiceProviderList.as_view()), name="serviceprovider-list"),
    path("admin/<int:pk>/", admin_list, name="admin-list"),
    path("attribute/<int:pk>/", attribute_list, name="attribute-list"),
    path("attribute/list/", attribute_admin_list, name="attribute-admin-list"),
    path("attribute/view/<int:pk>/", attribute_view, name="attribute-view"),
    path("certificate/<int:pk>/", certificate_list, name="certificate-list"),
    path("certificate/info/<int:pk>/", certificate_info, name="certificate-info"),
    path("certificate/list/", certificate_admin_list, name="certificate-admin-list"),
    path("contact/<int:pk>/", contact_list, name="contact-list"),
    path("endpoint/<int:pk>/", endpoint_list, name="endpoint-list"),
    path("email/", email_list, name="email-list"),
    path("metadata/import/", metadata_import, name="metadata-import"),
    path("metadata/manage/saml/", metadata_management, {"service_type": "saml"}, name="metadata-manage-saml"),
    path("metadata/manage/ldap/", metadata_management, {"service_type": "ldap"}, name="metadata-manage-ldap"),
    path("metadata/manage/oidc/", metadata_management, {"service_type": "oidc"}, name="metadata-manage-oidc"),
    path("metadata/<int:pk>/", metadata, name="metadata-view"),
    path("redirecturi/<int:pk>/", redirecturi_list, name="redirecturi-list"),
    path(
        "technical/<int:pk>/",
        login_required(SamlTechnicalInformationUpdate.as_view()),
        name="technical-update",
    ),
    path(
        "ldap/<int:pk>/",
        login_required(LdapTechnicalInformationUpdate.as_view()),
        name="ldap-technical-update",
    ),
    path(
        "oidc/<int:pk>/",
        login_required(OidcTechnicalInformationUpdate.as_view()),
        name="oidc-technical-update",
    ),
    path(
        "serviceprovider/add/saml/",
        login_required(SamlServiceProviderCreate.as_view()),
        name="saml-serviceprovider-add",
    ),
    path(
        "serviceprovider/add/ldap/",
        login_required(LdapServiceProviderCreate.as_view()),
        name="ldap-serviceprovider-add",
    ),
    path(
        "serviceprovider/add/oidc/",
        login_required(OidcServiceProviderCreate.as_view()),
        name="oidc-serviceprovider-add",
    ),
    path(
        "serviceprovider/remove/<int:pk>/",
        login_required(ServiceProviderDelete.as_view()),
        name="serviceprovider-delete",
    ),
    path(
        "serviceprovider/<int:pk>/",
        login_required(BasicInformationUpdate.as_view()),
        name="basicinformation-update",
    ),
    path("saml_admin_list/", login_required(SAMLAdminList.as_view()), name="saml-admin-list"),
    path("statistics/summary/", statistics_summary_list, name="statistics-summary-list"),
    path("statistics/<int:pk>/", statistics_list, name="statistics-list"),
    path("summary/<int:pk>/", login_required(BasicInformationView.as_view()), name="summary-view"),
    path("testuser/<int:pk>/", testuser_list, name="testuser-list"),
    path("testuser/data/<int:pk>/", testuser_attribute_data, name="testuser-attribute-data"),
    path("usergroup/<int:pk>/", usergroup_list, name="usergroup-list"),
    path("invite/", activate_key, name="invite-activate"),
    path("invite/<slug:invite_key>/", activate_key, name="invite-activate-key"),
    path("error/", sp_error, name="error"),
    path("", include("django.contrib.auth.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]
