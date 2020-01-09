import logging
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render

from rr.models.statistics import Statistics
from rr.models.serviceprovider import ServiceProvider
from rr.utils.serviceprovider import get_service_provider

logger = logging.getLogger(__name__)


@login_required
def statistics_list(request, pk):
    """
    Displays a list of :model:`rr.Statistics` linked to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Statistics`.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/statistics.html`
    """
    sp = get_service_provider(pk, request.user, service_type=["oidc", "saml"])
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


@login_required
def statistics_summary_list(request):
    """
    Displays a list of :model:`rr.Statistics` linked to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Statistics`.

    **Template:**

    :template:`rr/statistics_summary.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    serviceproviders = ServiceProvider.objects.filter(end_at=None,
                                                      production=True,
                                                      service_type="saml").order_by("entity_id")
    stats = Statistics.objects.all()
    statistics = []
    for sp in serviceproviders:
        weekly = stats.filter(sp=sp, date__gte=(date.today() - timedelta(days=8))
                              ).aggregate(Sum('logins')).get("logins__sum", 0)
        monthly = stats.filter(sp=sp, date__gte=(date.today() - timedelta(days=31))
                               ).aggregate(Sum('logins')).get("logins__sum", 0)
        six_months = stats.filter(sp=sp, date__gte=(date.today() - timedelta(days=183))
                              ).aggregate(Sum('logins')).get("logins__sum", 0)
        yearly = stats.filter(sp=sp, date__gte=(date.today() - timedelta(days=365))
                              ).aggregate(Sum('logins')).get("logins__sum", 0)
        statistics.append([sp.pk, sp.entity_id, weekly, monthly, six_months, yearly])
    return render(request, "rr/statistics_summary.html", {'object_list': statistics})
