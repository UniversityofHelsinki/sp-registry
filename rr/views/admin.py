from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from rr.models.admin import Keystore
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rr.models.serviceprovider import ServiceProvider
from rr.forms.admin import AdminForm
from django.http.response import Http404
from django.contrib.auth.models import User


@login_required
def admin_list(request, pk):
    """
    Displays a lists of :model:`auth.User` and :model:`rr.Keystore`
    linked to :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Keystore`.

    ``form``
        Form for sending an invitation

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/admin.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service provider does not exist")
    form = AdminForm()
    if request.method == "POST":
        if "add_invite" in request.POST:
            form = AdminForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                Keystore.objects.create_key(sp=sp, creator=request.user, email=email)
        elif "remove_invite" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    invite = Keystore.objects.get(pk=key)
                    if invite.sp == sp:
                        invite.delete()
        elif "remove_admin" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    admin = User.objects.get(pk=key)
                    sp.admins.remove(admin)
    invites = Keystore.objects.filter(sp=sp)
    return render(request, "rr/admin.html", {'object_list': invites,
                                             'form': form,
                                             'object': sp})


@login_required
def activate_key(request, invite_key=""):
    """
    Activates an :model:`rr.Keystore' adding
    :model:`auth.User` to :model:`rr.ServiceProvider`.

    Redirects to summary-view.
    """

    sp = Keystore.objects.activate_key(user=request.user,
                                       key=invite_key)
    if sp:
        return HttpResponseRedirect(reverse('summary-view', args=(sp,)))
    else:
        error_message = _("Activation key does not match")
        return render(request, "error.html", {'error_message': error_message})
