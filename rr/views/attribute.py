import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.forms.attribute import AttributeForm
from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute

logger = logging.getLogger(__name__)


@login_required
def attribute_list(request, pk):
    """
    Displays a form including all public :model:`rr.Attribute`
    and reasons if they are linked to :model:`rr.ServiceProvider`.

    If reason is given, links :model:`rr.Attribute` to
    :model:`rr.ServiceProvider` through
    :model:`rr.SPAttribute`.

    If reason is removed, adds end_at time for :model:`rr.SPAttribute`

    **Context**

    ``form``
        List of :model:`rr.SPAttribute`.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/attribute_list.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404(_("Service provider does not exist"))
    if request.method == "POST":
        form = AttributeForm(request.POST, sp=sp, is_admin=request.user.is_superuser)
        if form.is_valid():
            for field in form:
                data = form.cleaned_data.get(field.name)
                sp_attribute = SPAttribute.objects.filter(sp=sp, attribute__friendlyname=field.name,
                                                          end_at=None).first()
                if sp_attribute and not data:
                    sp_attribute.end_at = timezone.now()
                    sp_attribute.save()
                    sp.save_modified()
                    logger.info("Attribute requisition for {attribute} removed from {sp} by {user}"
                                .format(attribute=sp_attribute.attribute, sp=sp,
                                        user=request.user))
                elif data:
                    if not sp_attribute:
                        attribute = Attribute.objects.filter(friendlyname=field.name).first()
                        SPAttribute.objects.create(sp=sp, attribute=attribute, reason=data)
                        sp.save_modified()
                        logger.info("Attribute {attribute} requested for {sp} by {user}"
                                    .format(attribute=attribute, sp=sp, user=request.user))
                    else:
                        if sp_attribute.reason != data:
                            sp_attribute.reason = data
                            sp_attribute.save()
                            sp.save_modified()
                            logger.info("Attribute {attribute} reason updated for {sp} by {user}"
                                        .format(attribute=sp_attribute.attribute, sp=sp,
                                                user=request.user))
        form = AttributeForm(request.POST, sp=sp, is_admin=request.user.is_superuser)
    else:
        form = AttributeForm(sp=sp, is_admin=request.user.is_superuser)
    return render(request, "rr/attribute_list.html", {'form': form,
                                                      'object': sp})


@login_required
def attribute_admin_list(request):
    """
    Displays a list of :model:`rr.Attribute`.

    Only available for super users.

    **Context**

    ``object_list``
        List of :model:`rr.Attribute`.

    **Template:**

    :template:`rr/attribute_admin_list.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    attributes = Attribute.objects.all().order_by('friendlyname')
    return render(request, "rr/attribute_admin_list.html", {'object_list': attributes})


@login_required
def attribute_view(request, pk):
    """
    Displays an invidual :model:`rr.Attribute` and
    list of :model:`rr.ServiceProvider` linked
    to that attribute through :model:`rr.SPAttribute`.

    Only available for super users.

    **Context**

    ``object_list``
        List of :model:`rr.SPAttribute`.

    ``object``
        An instance of :model:`rr.Attribute`.

    **Template:**

    :template:`rr/attribute_admin_view.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    try:
        attribute = Attribute.objects.get(pk=pk)
    except ServiceProvider.DoesNotExist:
        raise Http404(_("Attribute proviced does not exist"))
    attributes = SPAttribute.objects.filter(attribute=attribute,
                                            end_at=None).order_by('sp__entity_id')
    return render(request, "rr/attribute_admin_view.html", {'object_list': attributes,
                                                            'attribute': attribute})
