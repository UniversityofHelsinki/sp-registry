"""
Missing data checks
"""

from django.urls.base import reverse
from django.utils.translation import ugettext as _

from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.redirecturi import RedirectUri


def _format_missing_message(links, msg, url=None):
    if links and url:
        return "<a href='" + url + "'>" + msg + "</a>"
    else:
        return msg


def _get_missing_saml_data(sp, missing, links):
    if not sp.privacypolicy_en and not sp.privacypolicy_fi and sp.attributes:
        msg = _("Privacy policy URL in English or in Finnish")
        url = reverse("basicinformation-update", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if not Certificate.objects.filter(sp=sp, end_at=None):
        msg = _("Certificate")
        url = reverse("certificate-list", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if not Endpoint.objects.filter(sp=sp, end_at=None,
                                   type='AssertionConsumerService'):
        msg = _("AssertionConsumerService endpoint")
        url = reverse("endpoint-list", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    return missing


def _get_missing_oidc_data(sp, missing, links):
    if not RedirectUri.objects.filter(sp=sp, end_at=None):
        msg = _("Redirect URI")
        url = reverse("redirecturi-list", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    return missing


def get_missing_sp_data(sp, links=True):
    """
    Returns list of missing data.

    sp: ServiceProvider object
    links (boolean): include html links in list
    """
    missing = []
    if not sp.name_en and not sp.name_fi:
        msg = _("Service name in English or in Finnish")
        url = reverse("basicinformation-update", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if not sp.description_en and not sp.description_fi:
        msg = _("Service description in English or in Finnish")
        url = reverse("basicinformation-update", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if not sp.application_portfolio:
        msg = _("Application portfolio URL")
        url = reverse("basicinformation-update", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if not Contact.objects.filter(sp=sp, end_at=None, type="technical"):
        msg = _("Technical contact")
        url = reverse("contact-list", args=[sp.pk])
        missing.append(_format_missing_message(links, msg, url))
    if sp.service_type == "saml":
        missing = _get_missing_saml_data(sp, missing, links)
    elif sp.service_type == "oidc":
        missing = _get_missing_oidc_data(sp, missing, links)
    return missing
