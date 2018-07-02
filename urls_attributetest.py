from django.conf.urls import url
from rr.views.attribute_test_service import attribute_test_service

# Overwrite default status handlers
handler400 = 'rr.views.handlers.bad_request'
handler403 = 'rr.views.handlers.permission_denied'
handler404 = 'rr.views.handlers.page_not_found'
handler500 = 'rr.views.handlers.server_error'

urlpatterns = [
    url(r'^$', attribute_test_service, name='attribute-test-service'),
]
