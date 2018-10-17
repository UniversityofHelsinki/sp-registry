import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _

from rr.forms.usergroup import UserGroupForm
from rr.models.serviceprovider import ServiceProvider
from rr.models.usergroup import UserGroup

logger = logging.getLogger(__name__)


@login_required
def usergroup_list(request, pk):
    """
    Displays a list of :model:`rr.UserGroup` linked to
    :model:`rr.ServiceProvider`.

    Includes a ModelForm for adding :model:`rr.UserGroup` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.UserGroup`.

    ``form``
        ModelForm for creating a :model:`rr.UserGroup`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/usergroup.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None, service_type="ldap")
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None,
                                             service_type="ldap")
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    form = UserGroupForm(sp=sp)
    if request.method == "POST":
        if "add_usergroup" in request.POST:
            form = UserGroupForm(request.POST, sp=sp)
            if form.is_valid():
                name = form.cleaned_data['name']
                UserGroup.objects.create(sp=sp, name=name)
                sp.save_modified()
                logger.info("User group added for {sp} by {user}".format(sp=sp, user=request.user))
                form = UserGroupForm(sp=sp)
                messages.add_message(request, messages.INFO, _('User group added.'))
        elif "remove_usergroup" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    user_group = UserGroup.objects.get(pk=key)
                    if user_group.sp == sp:
                        user_group.end_at = timezone.now()
                        user_group.save()
                        sp.save_modified()
                        logger.info("User group removed from {sp} by {user}".format(
                            sp=sp, user=request.user))
                        messages.add_message(request, messages.INFO, _('User group removed.'))
    contacts = UserGroup.objects.filter(sp=sp, end_at=None).order_by('name')
    return render(request, "rr/usergroup.html", {'object_list': contacts,
                                                 'form': form,
                                                 'object': sp})
