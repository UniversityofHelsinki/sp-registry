import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _

from rr.forms.endpoint import EndpointForm
from rr.models.endpoint import Endpoint
from rr.utils.serviceprovider import get_service_provider

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
    sp = get_service_provider(pk, request.user, service_type=["saml"])
    form = EndpointForm(sp=sp)
    if request.method == "POST":
        if "add_endpoint" in request.POST:
            form = _add_endpoint(request, sp)
        elif "remove_endpoint" in request.POST:
            _remove_endpoints(request, sp)
    endpoints = Endpoint.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/endpoint.html", {"object_list": endpoints, "form": form, "object": sp})


def _add_endpoint(request, sp):
    form = EndpointForm(request.POST, sp=sp)
    if form.is_valid():
        contact_type = form.cleaned_data["type"]
        binding = form.cleaned_data["binding"]
        location = form.cleaned_data["location"]
        response_location = form.cleaned_data["response_location"]
        index = form.cleaned_data["index"]
        is_default = form.cleaned_data["is_default"]
        Endpoint.objects.create(
            sp=sp,
            type=contact_type,
            binding=binding,
            location=location,
            response_location=response_location,
            index=index,
            is_default=is_default,
        )
        sp.save_modified()
        logger.info("Endpoint added for {sp} by {user}".format(sp=sp, user=request.user))
        messages.add_message(request, messages.INFO, _("Endpoint added."))
        form = EndpointForm(sp=sp)
    return form


def _remove_endpoints(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            endpoint = Endpoint.objects.get(pk=key)
            if endpoint.sp == sp:
                endpoint.end_at = timezone.now()
                endpoint.save()
                sp.save_modified()
                logger.info("Endpoint removed from {sp} by {user}".format(sp=sp, user=request.user))
                messages.add_message(request, messages.INFO, _("Endpoint removed."))
