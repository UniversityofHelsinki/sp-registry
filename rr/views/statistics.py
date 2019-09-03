import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import render

from rr.models.statistics import Statistics
from rr.models.serviceprovider import ServiceProvider

logger = logging.getLogger(__name__)


@login_required
def statistics_list(request, pk):
    """
    Displays a list of :model:`rr.Statistics` linked to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Endpoint`.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/statistics.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None, service_type="saml")
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None,
                                             service_type="saml")
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    try:
        days = int(request.GET.get('days', 31))
    except ValueError:
        days = 31
    if days == 0:
        statistics = Statistics.objects.filter(sp=sp)
    else:
        date_start = (date.today() - timedelta(days=days + 1))
        statistics = Statistics.objects.filter(sp=sp, date__gte=date_start)
    return render(request, "rr/statistics.html", {'object_list': statistics,
                                                  'object': sp,
                                                  'days': days})
