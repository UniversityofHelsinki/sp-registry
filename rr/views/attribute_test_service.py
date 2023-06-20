from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.http.response import Http404
from django.shortcuts import render
from django.utils.translation import gettext as _

from rr.models.attribute import Attribute


def attribute_test_service(request):
    """
    Displays a list of all :model:`rr.Attribute` and values
    found from environment variables.
    **Context**

    ``object_list``
        List of dictionaries containing attribute values and metadata.

    ``logout_url``
        Logout URL.

    **Template:**

    :template:`attribute_test_service.html`
    """
    if not hasattr(settings, "ATTRIBUTE_TEST_SERVICE") or not settings.ATTRIBUTE_TEST_SERVICE:
        raise Http404(_("Attribute test service has been disabled"))
    attributes = Attribute.objects.filter(test_service=True).order_by("friendlyname")
    object_list = []
    for attribute in attributes:
        value = request.META.get(attribute.shib_env, "").encode("latin1").decode("utf-8", "ignore")
        regex = attribute.regex_test
        icon = _check_status(attribute, value, regex)
        if attribute.public_saml or value:
            object_list.append(
                {
                    "friendlyname": attribute.friendlyname,
                    "name": attribute.name,
                    "value": value.replace(";", "<br>"),
                    "regex": regex,
                    "icon": icon,
                }
            )
    if hasattr(settings, "ATTRIBUTE_TEST_SERVICE_LOGOUT_URL"):
        logout_url = settings.ATTRIBUTE_TEST_SERVICE_LOGOUT_URL
    else:
        logout_url = None
    return render(
        request,
        "attribute_test_service.html",
        {
            "object_list": object_list,
            "logout_url": logout_url,
            "shib_auth_context": request.META.get("Shib-AuthnContext-Class", ""),
            "shib_auth_method": request.META.get("Shib-Authentication-Method", ""),
        },
    )


def _check_status(attribute, value, regex):
    if value:
        if regex:
            try:
                RegexValidator(regex)(value)
                icon = "valid"
            except ValidationError:
                icon = "invalid"
        else:
            icon = "valid"
    else:
        if attribute.test_service_required:
            icon = "invalid"
        else:
            icon = "optional"
    return icon
