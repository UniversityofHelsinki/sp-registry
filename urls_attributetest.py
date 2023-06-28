from django.conf.urls import include, url

from rr.views.attribute_test_service import attribute_test_service
from rr.views.sp_errors import sp_error

# Overwrite default status handlers
handler400 = "rr.views.handlers.bad_request_blank"
handler403 = "rr.views.handlers.permission_denied_blank"
handler404 = "rr.views.handlers.page_not_found_blank"
handler500 = "rr.views.handlers.server_error_blank"

urlpatterns = [
    url(r"^error/$", sp_error, name="error"),
    url(r"^$", attribute_test_service, name="attribute-test-service"),
    url(r"^i18n/", include("django.conf.urls.i18n")),
]
