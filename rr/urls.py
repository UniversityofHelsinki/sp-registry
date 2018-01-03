"""rr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from rr.views.serviceprovider import BasicInformationCreate, BasicInformationUpdate, BasicInformationView, ServiceProviderList
from rr.views.attribute import attribute_list
from rr.views.certificate import certificate_list
from rr.views.contact import contact_list
from rr.views.endpoint import endpoint_list
from rr.views.metadata import metadata

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', login_required(ServiceProviderList.as_view()), name='serviceprovider-list'),
    url(r'attribute/(?P<pk>[0-9]+)/$', attribute_list, name='attribute-list'),
    url(r'certificate/(?P<pk>[0-9]+)/$', certificate_list, name='certificate-list'),
    url(r'contact/(?P<pk>[0-9]+)/$', contact_list, name='contact-list'),
    url(r'endpoint/(?P<pk>[0-9]+)/$', endpoint_list, name='endpoint-list'),
    url(r'metadata/(?P<pk>[0-9]+)/$', metadata, name='metadata-view'),
    url(r'serviceprovider/add/$', login_required(BasicInformationCreate.as_view()), name='basicinformation-add'),
    url(r'serviceprovider/(?P<pk>[0-9]+)/$', login_required(BasicInformationView.as_view()), name='basicinformation-view'),
    url(r'serviceprovider/update/(?P<pk>[0-9]+)/$', login_required(BasicInformationUpdate.as_view()), name='basicinformation-update'),
]
