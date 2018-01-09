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
    attributes = Attribute.objects.filter(public=True)
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user)
    except ServiceProvider.DoesNotExist:
        raise Http404(_("Service proviced does not exist"))
    if request.method == "POST":
        form = AttributeForm(request.POST, sp=sp)
        if form.is_valid():
            for field in form:
                data = form.cleaned_data.get(field.name)
                sp_attribute = SPAttribute.objects.filter(sp=sp, attribute__friendlyname=field.name).first()
                if sp_attribute and not data:
                    sp_attribute.delete()
                elif data:
                    if not sp_attribute:
                        attribute = Attribute.objects.filter(friendlyname=field.name).first()
                        SPAttribute.objects.create(sp=sp, attribute=attribute, reason=data, updated=timezone.now())
                    else:
                        if sp_attribute.reason != data:
                            sp_attribute.reason = data
                            sp_attribute.save()
        form = AttributeForm(request.POST, sp=sp)
    else:
        form = AttributeForm(sp=sp)
    return render(request, "rr/attribute_list.html", {'object_list': attributes,
                                                 'form': form,
                                                 'object': sp})


@login_required
def attribute_admin_list(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    attributes = Attribute.objects.filter()
    return render(request, "rr/attribute_admin_list.html", {'object_list': attributes})


@login_required
def attribute_view(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    try:
        attribute = Attribute.objects.get(pk=pk)
    except ServiceProvider.DoesNotExist:
        raise Http404(_("Attribute proviced does not exist"))
    attributes = SPAttribute.objects.filter(attribute=attribute).order_by('sp__entity_id')
    return render(request, "rr/attribute_view.html", {'object_list': attributes,
                                                 'object': attribute})
