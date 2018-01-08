from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.forms.attribute import AttributeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import Http404
from django.utils import timezone


@login_required
def attribute_list(request, pk):
    attributes = Attribute.objects.filter(public=True)
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service proviced does not exist")
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
    return render(request, "rr/attribute.html", {'object_list': attributes,
                                                 'form': form,
                                                 'object': sp})
