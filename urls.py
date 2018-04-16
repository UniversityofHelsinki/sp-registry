from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.decorators import login_required
from rr.views.serviceprovider import BasicInformationCreate, BasicInformationUpdate, BasicInformationView,\
    ServiceProviderDelete, ServiceProviderList, TechnicalInformationUpdate,\
    SingEncryptList, LdapTechnicalInformationUpdate
from rr.views.attribute import attribute_list, attribute_admin_list, attribute_view
from rr.views.certificate import certificate_list, certificate_admin_list
from rr.views.contact import contact_list
from rr.views.endpoint import endpoint_list
from rr.views.metadata import metadata, metadata_import, metadata_management
from rr.views.login import ShibbolethLoginView
from rr.views.spadmin import activate_key, admin_list
from rr.views.testuser import testuser_list, testuser_attribute_data
from rr.views.usergroup import usergroup_list

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
    url(r'^logout/$', LogoutView.as_view(template_name="registration/logout.html"), name='logout'),
    url(r'^list/$', login_required(ServiceProviderList.as_view()), name='serviceprovider-list'),
    url(r'^admin/(?P<pk>[0-9]+)/$', admin_list, name='admin-list'),
    url(r'^attribute/(?P<pk>[0-9]+)/$', attribute_list, name='attribute-list'),
    url(r'^attribute/list/$', attribute_admin_list, name='attribute-admin-list'),
    url(r'^attribute/view/(?P<pk>[0-9]+)/$', attribute_view, name='attribute-view'),
    url(r'^certificate/(?P<pk>[0-9]+)/$', certificate_list, name='certificate-list'),
    url(r'^certificate/list/$', certificate_admin_list, name='certificate-admin-list'),
    url(r'^contact/(?P<pk>[0-9]+)/$', contact_list, name='contact-list'),
    url(r'^endpoint/(?P<pk>[0-9]+)/$', endpoint_list, name='endpoint-list'),
    url(r'^metadata/import/$', metadata_import, name='metadata-import'),
    url(r'^metadata/manage/$', metadata_management, name='metadata-manage'),
    url(r'^metadata/(?P<pk>[0-9]+)/$', metadata, name='metadata-view'),
    url(r'^technical/(?P<pk>[0-9]+)/$', login_required(TechnicalInformationUpdate.as_view()), name='technical-update'),
    url(r'^ldap/(?P<pk>[0-9]+)/$', login_required(LdapTechnicalInformationUpdate.as_view()), name='ldap-technical-update'),
    url(r'^serviceprovider/add/$', login_required(BasicInformationCreate.as_view()), name='serviceprovider-add'),
    url(r'^serviceprovider/remove/(?P<pk>[0-9]+)/$', login_required(ServiceProviderDelete.as_view()), name='serviceprovider-delete'),
    url(r'^serviceprovider/(?P<pk>[0-9]+)/$', login_required(BasicInformationUpdate.as_view()), name='basicinformation-update'),
    url(r'^sign_encrypt_list/$', login_required(SingEncryptList.as_view()), name='sign-encrypt-list'),
    url(r'^summary/(?P<pk>[0-9]+)/$', login_required(BasicInformationView.as_view()), name='summary-view'),
    url(r'^testuser/(?P<pk>[0-9]+)/$', testuser_list, name='testuser-list'),
    url(r'^testuser/data/(?P<pk>[0-9]+)/$', testuser_attribute_data, name='testuser-attribute-data'),
    url(r'^usergroup/(?P<pk>[0-9]+)/$', usergroup_list, name='usergroup-list'),
    url(r'^invite/$', activate_key, name='invite-activate'),
    url(r'^invite/(?P<invite_key>[\w+\s-]+)/$', activate_key, name='invite-activate-key'),
    url('^', include('django.contrib.auth.urls')),
]
