from django.conf.urls import url, include
from rr.views.attribute_test_service import attribute_test_service

# Overwrite default status handlers
handler400 = 'rr.views.handlers.bad_request_blank'
handler403 = 'rr.views.handlers.permission_denied_blank'
handler404 = 'rr.views.handlers.page_not_found_blank'
handler500 = 'rr.views.handlers.server_error_blank'

urlpatterns = [
    url(r'^$', attribute_test_service, name='attribute-test-service'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]
