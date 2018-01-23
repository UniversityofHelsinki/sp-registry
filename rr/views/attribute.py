from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.forms.attribute import AttributeForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.http.response import Http404
from django.utils import timezone
from django.core.exceptions import PermissionDenied


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
        raise Http404(_("Service provider does not exist"))
    if request.method == "POST":
        form = AttributeForm(request.POST, sp=sp)
        if form.is_valid():
            for field in form:
                data = form.cleaned_data.get(field.name)
                sp_attribute = SPAttribute.objects.filter(sp=sp, attribute__friendlyname=field.name, end_at=None).first()
                if sp_attribute and not data:
                    sp_attribute.end_at = timezone.now()
                    sp_attribute.save()
                    sp.modified = True
                    sp.save()
                elif data:
                    if not sp_attribute:
                        attribute = Attribute.objects.filter(friendlyname=field.name).first()
                        SPAttribute.objects.create(sp=sp,
                                                   attribute=attribute,
                                                   reason=data)
                        sp.modified = True
                        sp.save()
                    else:
                        if sp_attribute.reason != data:
                            sp_attribute.reason = data
                            sp_attribute.save()
                            sp.modified = True
                            sp.save()
        form = AttributeForm(request.POST, sp=sp)
    else:
        form = AttributeForm(sp=sp)
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
    attributes = Attribute.objects.filter()
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

    :template:`rr/attribute_view.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    try:
        attribute = Attribute.objects.get(pk=pk)
    except ServiceProvider.DoesNotExist:
        raise Http404(_("Attribute proviced does not exist"))
    attributes = SPAttribute.objects.filter(attribute=attribute, end_at=None).order_by('sp__entity_id')
    return render(request, "rr/attribute_view.html", {'object_list': attributes,
                                                      'object': attribute})
