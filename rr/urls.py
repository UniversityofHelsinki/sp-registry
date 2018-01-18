
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from rr.views.serviceprovider import BasicInformationCreate, BasicInformationUpdate, BasicInformationView, ServiceProviderList
from rr.views.attribute import attribute_list, attribute_admin_list, attribute_view
from rr.views.certificate import certificate_list
from rr.views.contact import contact_list
from rr.views.endpoint import endpoint_list
from rr.views.metadata import metadata
from rr.views.basic import FrontPage, CustomLoginView
from rr.views.admin import activate_key, admin_list

urlpatterns = [
    url(r'^admin_django/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin_django/', admin.site.urls),
    url(r'^$', login_required(ServiceProviderList.as_view()), name='front-page'),
    url(r'^login/$', CustomLoginView.as_view(), name='login'),
    url(r'^list/$', login_required(ServiceProviderList.as_view()), name='serviceprovider-list'),
    url(r'^admin/(?P<pk>[0-9]+)/$', admin_list, name='admin-list'),
    url(r'^attribute/(?P<pk>[0-9]+)/$', attribute_list, name='attribute-list'),
    url(r'^attribute/list/$', attribute_admin_list, name='attribute-admin-list'),
    url(r'^attribute/view/(?P<pk>[0-9]+)/$', attribute_view, name='attribute-view'),
    url(r'^certificate/(?P<pk>[0-9]+)/$', certificate_list, name='certificate-list'),
    url(r'^contact/(?P<pk>[0-9]+)/$', contact_list, name='contact-list'),
    url(r'^endpoint/(?P<pk>[0-9]+)/$', endpoint_list, name='endpoint-list'),
    url(r'^metadata/(?P<pk>[0-9]+)/$', metadata, name='metadata-view'),
    url(r'^serviceprovider/add/$', login_required(BasicInformationCreate.as_view()), name='serviceprovider-add'),
    url(r'^serviceprovider/update/(?P<pk>[0-9]+)/$', login_required(BasicInformationUpdate.as_view()), name='basicinformation-update'),
    url(r'^summary/(?P<pk>[0-9]+)/$', login_required(BasicInformationView.as_view()), name='summary-view'),
    url(r'^invite/(?P<invite_key>[\w+\s-]+)/$', activate_key, name='invite-activate'),
    url('^', include('django.contrib.auth.urls')),
]
