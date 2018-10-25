from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.decorators import login_required

from rr.views.serviceprovider import SamlServiceProviderCreate, BasicInformationUpdate
from rr.views.serviceprovider import BasicInformationView, ServiceProviderDelete
from rr.views.serviceprovider import ServiceProviderList, TechnicalInformationUpdate
from rr.views.serviceprovider import SingEncryptList
from rr.views.serviceprovider import LdapServiceProviderCreate, LdapTechnicalInformationUpdate
from rr.views.attribute import attribute_list, attribute_admin_list, attribute_view
from rr.views.certificate import certificate_list, certificate_admin_list
from rr.views.certificate import certificate_info
from rr.views.contact import contact_list
from rr.views.endpoint import endpoint_list
from rr.views.metadata import metadata, metadata_import, metadata_management
from rr.views.login import ShibbolethLoginView, logout_redirect
from rr.views.spadmin import activate_key, admin_list
from rr.views.testuser import testuser_list, testuser_attribute_data
from rr.views.usergroup import usergroup_list
from rr.views.email import email_list

# Overwrite default status handlers
handler400 = 'rr.views.handlers.bad_request'
handler403 = 'rr.views.handlers.permission_denied'
handler404 = 'rr.views.handlers.page_not_found'
handler500 = 'rr.views.handlers.server_error'

urlpatterns = [
    url(r'^admin_django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin_django/', admin.site.urls),
    url(r'^$', login_required(ServiceProviderList.as_view()), name='front-page'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^login/shibboleth/$', ShibbolethLoginView.as_view(), name='shibboleth-login'),
    url(r'^logout/$', logout_redirect, name='logout'),
    url(r'^logout/local/$', LogoutView.as_view(template_name="registration/logout.html",
                                               redirect_field_name='return'), name='logout-local'),
    url(r'^list/$', login_required(ServiceProviderList.as_view()), name='serviceprovider-list'),
    url(r'^admin/(?P<pk>[0-9]+)/$', admin_list, name='admin-list'),
    url(r'^attribute/(?P<pk>[0-9]+)/$', attribute_list, name='attribute-list'),
    url(r'^attribute/list/$', attribute_admin_list, name='attribute-admin-list'),
    url(r'^attribute/view/(?P<pk>[0-9]+)/$', attribute_view, name='attribute-view'),
    url(r'^certificate/(?P<pk>[0-9]+)/$', certificate_list, name='certificate-list'),
    url(r'^certificate/info/(?P<pk>[0-9]+)/$', certificate_info, name='certificate-info'),
    url(r'^certificate/list/$', certificate_admin_list, name='certificate-admin-list'),
    url(r'^contact/(?P<pk>[0-9]+)/$', contact_list, name='contact-list'),
    url(r'^endpoint/(?P<pk>[0-9]+)/$', endpoint_list, name='endpoint-list'),
    url(r'^email/$', email_list, name='email-list'),
    url(r'^metadata/import/$', metadata_import, name='metadata-import'),
    url(r'^metadata/manage/saml/$', metadata_management, {'service_type': 'saml'},
        name='metadata-manage-saml'),
    url(r'^metadata/manage/ldap/$', metadata_management, {'service_type': 'ldap'},
        name='metadata-manage-ldap'),
    url(r'^metadata/(?P<pk>[0-9]+)/$', metadata, name='metadata-view'),
    url(r'^technical/(?P<pk>[0-9]+)/$', login_required(TechnicalInformationUpdate.as_view()),
        name='technical-update'),
    url(r'^ldap/(?P<pk>[0-9]+)/$', login_required(LdapTechnicalInformationUpdate.as_view()),
        name='ldap-technical-update'),
    url(r'^serviceprovider/add/saml/$', login_required(SamlServiceProviderCreate.as_view()),
        name='saml-serviceprovider-add'),
    url(r'^serviceprovider/add/ldap/$', login_required(LdapServiceProviderCreate.as_view()),
        name='ldap-serviceprovider-add'),
    url(r'^serviceprovider/remove/(?P<pk>[0-9]+)/$',
        login_required(ServiceProviderDelete.as_view()), name='serviceprovider-delete'),
    url(r'^serviceprovider/(?P<pk>[0-9]+)/$', login_required(BasicInformationUpdate.as_view()),
        name='basicinformation-update'),
    url(r'^sign_encrypt_list/$', login_required(SingEncryptList.as_view()),
        name='sign-encrypt-list'),
    url(r'^summary/(?P<pk>[0-9]+)/$', login_required(BasicInformationView.as_view()),
        name='summary-view'),
    url(r'^testuser/(?P<pk>[0-9]+)/$', testuser_list, name='testuser-list'),
    url(r'^testuser/data/(?P<pk>[0-9]+)/$', testuser_attribute_data,
        name='testuser-attribute-data'),
    url(r'^usergroup/(?P<pk>[0-9]+)/$', usergroup_list, name='usergroup-list'),
    url(r'^invite/$', activate_key, name='invite-activate'),
    url(r'^invite/(?P<invite_key>[\w+\s-]+)/$', activate_key, name='invite-activate-key'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
