import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.forms.attribute import AttributeForm
from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.utils.serviceprovider import get_service_provider

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
    sp = get_service_provider(pk, request.user)
    if request.method == "POST":
        form = AttributeForm(request.POST, sp=sp, is_admin=request.user.is_superuser)
        if form.is_valid():
            _check_form(request, sp, form)
            form = AttributeForm(sp=sp, is_admin=request.user.is_superuser)
        else:
            form = AttributeForm(request.POST, sp=sp, is_admin=request.user.is_superuser)
    else:
        form = AttributeForm(sp=sp, is_admin=request.user.is_superuser)
    return render(request, "rr/attribute_list.html", {"form": form, "object": sp})


def _check_form(request, sp, form):
    removed_attributes = []
    added_attributes = []
    modified_attributes = []
    for field in form:
        if not field.name.startswith("extra_"):
            data = form.cleaned_data.get(field.name)
            sp_attribute = SPAttribute.objects.filter(sp=sp, attribute__friendlyname=field.name, end_at=None).first()
            userinfo, id_token = _get_oidc_fields(sp, form, field)
            if sp_attribute and not data:
                sp_attribute.end_at = timezone.now()
                sp_attribute.save()
                sp.save_modified()
                logger.info(
                    "Attribute requisition for {attribute} removed from {sp} by {user}".format(
                        attribute=sp_attribute.attribute, sp=sp, user=request.user
                    )
                )
                removed_attributes.append(field.name)
            elif data and not sp_attribute:
                attribute = Attribute.objects.filter(friendlyname=field.name).first()
                SPAttribute.objects.create(
                    sp=sp, attribute=attribute, reason=data, oidc_userinfo=userinfo, oidc_id_token=id_token
                )
                sp.save_modified()
                logger.info(
                    "Attribute {attribute} requested for {sp} by {user}".format(
                        attribute=attribute, sp=sp, user=request.user
                    )
                )
                added_attributes.append(field.name)
            elif (
                data
                and sp_attribute
                and (
                    sp_attribute.reason != data
                    or sp_attribute.oidc_userinfo != userinfo
                    or sp_attribute.oidc_id_token != id_token
                )
            ):
                sp_attribute.reason = data
                sp_attribute.oidc_userinfo = userinfo
                sp_attribute.oidc_id_token = id_token
                sp_attribute.save()
                sp.save_modified()
                logger.info(
                    "Attribute {attribute} updated for {sp} by {user}".format(
                        attribute=sp_attribute.attribute, sp=sp, user=request.user
                    )
                )
                modified_attributes.append(field.name)
    _create_messages(request, added_attributes, modified_attributes, removed_attributes)


def _create_messages(request, added_attributes, modified_attributes, removed_attributes):
    if added_attributes:
        messages.add_message(request, messages.INFO, _("Attributes added: ") + ", ".join(added_attributes))
    if modified_attributes:
        messages.add_message(request, messages.INFO, _("Attributes modified: ") + ", ".join(modified_attributes))
    if removed_attributes:
        messages.add_message(request, messages.INFO, _("Attributes removed: ") + ", ".join(removed_attributes))


def _get_oidc_fields(sp, form, field):
    if sp.service_type == "oidc":
        userinfo = form.cleaned_data.get("extra_userinfo_" + field.name)
        id_token = form.cleaned_data.get("extra_id_token_" + field.name)
    else:
        userinfo = False
        id_token = False
    return userinfo, id_token


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
    attributes = Attribute.objects.all().order_by("friendlyname")
    return render(request, "rr/attribute_admin_list.html", {"object_list": attributes})


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
        raise Http404(_("Attribute provided does not exist"))
    attributes = SPAttribute.objects.filter(attribute=attribute, end_at=None, sp__end_at=None).order_by(
        "sp__entity_id"
    )
    return render(request, "rr/attribute_admin_view.html", {"object_list": attributes, "attribute": attribute})
