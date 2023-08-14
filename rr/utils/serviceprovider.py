import logging

from django.conf import settings
from django.db.models import Q
from django.http.response import Http404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rr.models.serviceprovider import ServiceProvider

logger = logging.getLogger(__name__)


def get_service_provider(pk, user, service_type=None, raise_404=True):
    """
    Get service provider if user has permissions

    pk: service provider pk
    user: current user
    service_type: limit to type if given
    raise_404: raise 404 error by default, if user has not permissions

    return: service provider object or None
    """
    try:
        if user.is_superuser:
            if service_type:
                sp = ServiceProvider.objects.get(pk=pk, end_at=None, service_type__in=service_type)
            else:
                sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            if service_type:
                sp = (
                    ServiceProvider.objects.filter(
                        (Q(admins=user) | Q(admin_groups__in=user.groups.all())),
                        pk=pk,
                        end_at=None,
                        service_type__in=service_type,
                    )
                    .distinct()
                    .last()
                )
            else:
                sp = (
                    ServiceProvider.objects.filter(
                        (Q(admins=user) | Q(admin_groups__in=user.groups.all())), pk=pk, end_at=None
                    )
                    .distinct()
                    .last()
                )
            if not sp:
                raise ServiceProvider.DoesNotExist
    except ServiceProvider.DoesNotExist:
        if raise_404:
            logger.debug("Tried to access unauthorized service provider")
            raise Http404(_("Service provider does not exist"))
        else:
            sp = None
    return sp


def get_service_provider_queryset(request, service_type=None):
    """
    Get service provider queryset if user has permissions

    request: request
    service_type: limit to type if given

    return: service provider queryset
    """
    user = request.user
    read_all_group = settings.READ_ALL_GROUP if hasattr(settings, "READ_ALL_GROUP") else None

    if user.is_superuser or (
        request.method == "GET" and read_all_group and user.groups.filter(name=read_all_group).exists()
    ):
        if service_type:
            return (
                ServiceProvider.objects.filter(end_at=None, service_type=service_type)
                .order_by("entity_id")
                .prefetch_related("admins", "admin_groups")
            )
        else:
            return (
                ServiceProvider.objects.filter(end_at=None)
                .order_by("entity_id")
                .prefetch_related("admins", "admin_groups")
            )
    else:
        if service_type:
            return (
                ServiceProvider.objects.filter(
                    (Q(admins=user) | Q(admin_groups__in=user.groups.all())), service_type=service_type, end_at=None
                )
                .distinct()
                .order_by("entity_id")
            ).prefetch_related("admins", "admin_groups")
        else:
            return (
                ServiceProvider.objects.filter((Q(admins=user) | Q(admin_groups__in=user.groups.all())), end_at=None)
                .distinct()
                .order_by("entity_id")
            ).prefetch_related("admins", "admin_groups")


def create_sp_history_copy(sp):
    """
    Create a history copy of SP, with end_at value and new pk

    return: created service provider object
    """
    admins = sp.admins.all()
    admin_groups = sp.admin_groups.all()
    nameidformat = sp.nameidformat.all()
    grant_types = sp.grant_types.all()
    response_types = sp.response_types.all()
    oidc_scopes = sp.oidc_scopes.all()
    sp.history = sp.pk
    sp.pk = None
    sp.end_at = timezone.now()
    sp.save()
    sp.admins.set(admins)
    sp.admin_groups.set(admin_groups)
    sp.nameidformat.set(nameidformat)
    sp.grant_types.set(grant_types)
    sp.response_types.set(response_types)
    sp.oidc_scopes.set(oidc_scopes)
    return sp
