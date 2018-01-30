from rr.models.serviceprovider import ServiceProvider
from rr.models.endpoint import Endpoint
from rr.forms.endpoint import EndpointForm
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


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
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    form = EndpointForm(sp=sp)
    if request.method == "POST":
        if "add_endpoint" in request.POST:
            form = EndpointForm(request.POST, sp=sp)
            if form.is_valid():
                contact_type = form.cleaned_data['type']
                binding = form.cleaned_data['binding']
                url = form.cleaned_data['url']
                index = form.cleaned_data['index']
                Endpoint.objects.create(sp=sp,
                                        type=contact_type,
                                        binding=binding,
                                        url=url,
                                        index=index)
                sp.modified = True
                sp.save()
                logger.info("Endpoint added for {sp} by {user}".format(sp=sp, user=request.user))
                form = EndpointForm(sp=sp)
        elif "remove_endpoint" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    endpoint = Endpoint.objects.get(pk=key)
                    if endpoint.sp == sp:
                        endpoint.end_at = timezone.now()
                        endpoint.save()
                        sp.modified = True
                        sp.save()
                        logger.info("Endpoint removed from {sp} by {user}".format(sp=sp, user=request.user))
    endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/endpoint.html", {'object_list': endpoints,
                                                'form': form,
                                                'object': sp})
