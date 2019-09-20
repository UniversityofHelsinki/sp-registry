import logging
from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import ServiceProvider

logger = logging.getLogger(__name__)


def get_service_provider(pk, user, service_type=None):
    try:
        if user.is_superuser:
            if service_type:
                sp = ServiceProvider.objects.get(pk=pk, end_at=None, service_type__in=service_type)
            else:
                sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            if service_type:
                sp = ServiceProvider.objects.get(pk=pk, admins=user, end_at=None, service_type__in=service_type)
            else:
                sp = ServiceProvider.objects.get(pk=pk, admins=user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404(_("Service provider does not exist"))
    return sp
