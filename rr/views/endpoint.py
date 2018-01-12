from rr.models.serviceprovider import ServiceProvider
from rr.models.endpoint import Endpoint
from rr.forms.endpoint import EndpointForm
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def endpoint_list(request, pk):
    """
    Displays a list of :model:`rr.Endpoint` linked to
    :model:`rr.ServiceProvider`.

    Includes a ModelForm for adding :model:`rr.Endpoint` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Endpoint`.

    ``form``
        ModelForm for creating a :model:`rr.Endpoint`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/endpoint.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service proviced does not exist")
    if request.method == "POST":
        if "add_endpoint" in request.POST:
            form = EndpointForm(request.POST)
            if form.is_valid():
                contact_type = form.cleaned_data['type']
                binding = form.cleaned_data['binding']
                url = form.cleaned_data['url']
                Endpoint.objects.create(sp=sp,
                                        type=contact_type,
                                        binding=binding,
                                        url=url)
                sp.modified = True
                sp.save()
        else:
            form = EndpointForm()
            # For certificate removal, check for the first POST item after csrf
            if (list(request.POST.dict().values())[1]) == "Remove":
                endpoint_id = list(request.POST.dict().keys())[1]
                endpoint = Endpoint.objects.get(pk=endpoint_id)
                if endpoint.sp == sp:
                    endpoint.end_at = timezone.now()
                    endpoint.save()
                    sp.modified = True
                    sp.save()
    else:
        form = EndpointForm()
    endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/endpoint.html", {'object_list': endpoints,
                                                'form': form,
                                                'object': sp})
