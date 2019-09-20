import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.forms.redirecturi import RedirectUriForm
from rr.models.redirecturi import RedirectUri
from rr.utils.serviceprovider import get_service_provider

logger = logging.getLogger(__name__)


@login_required
def redirecturi_list(request, pk):
    """
    Displays a list of :model:`rr.RedirectUri` linked to
    :model:`rr.ServiceProvider`.

    Includes a ModelForm for adding :model:`rr.RedirectUri` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.RedirectUri`.

    ``form``
        ModelForm for creating a :model:`rr.RedirectUri`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/redirecturi.html`
    """
    sp = get_service_provider(pk, request.user, service_type=["oidc"])
    form = RedirectUriForm(sp=sp)
    if request.method == "POST":
        if "add_redirecturi" in request.POST:
            form = _add_redirecturi(request, sp)
        elif "remove_redirecturi" in request.POST:
            _remove_redirecturis(request, sp)
    redirect_uris = RedirectUri.objects.filter(sp=sp, end_at=None).order_by('uri')
    return render(request, "rr/redirecturi.html", {'object_list': redirect_uris,
                                                   'form': form,
                                                   'object': sp})


def _add_redirecturi(request, sp):
    form = RedirectUriForm(request.POST, sp=sp)
    if form.is_valid():
        uri = form.cleaned_data['uri']
        RedirectUri.objects.create(sp=sp, uri=uri)
        sp.save_modified()
        logger.info("Redirect URL added for {sp} by {user}".format(sp=sp, user=request.user))
        form = RedirectUriForm(sp=sp)
        messages.add_message(request, messages.INFO, _('Redirect URL added.'))
    return form


def _remove_redirecturis(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            user_group = RedirectUri.objects.get(pk=key)
            if user_group.sp == sp:
                user_group.end_at = timezone.now()
                user_group.save()
                sp.save_modified()
                logger.info("Redirect URL removed from {sp} by {user}".format(
                    sp=sp, user=request.user))
                messages.add_message(request, messages.INFO, _('Redirect URL removed.'))
