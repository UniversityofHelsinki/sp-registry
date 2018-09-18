import logging

from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone

from rr.forms.contact import ContactForm
from rr.models.contact import Contact
from rr.models.serviceprovider import ServiceProvider

logger = logging.getLogger(__name__)


@login_required
def contact_list(request, pk):
    """
    Displays a list of :model:`rr.Contact` linked to
    :model:`rr.ServiceProvider`.

    Includes a ModelForm for adding :model:`rr.Contact` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Contact`.

    ``form``
        ModelForm for creating a :model:`rr.Contact`

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/contact.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    form = ContactForm(sp=sp)
    if request.method == "POST":
        if "add_contact" in request.POST:
            form = ContactForm(request.POST, sp=sp)
            if form.is_valid():
                contact_type = form.cleaned_data['type']
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                email = form.cleaned_data['email']
                Contact.objects.create(sp=sp,
                                       type=contact_type,
                                       firstname=firstname,
                                       lastname=lastname,
                                       email=email)
                sp.save_modified()
                logger.info("Contact added for {sp} by {user}"
                            .format(sp=sp, user=request.user))
                form = ContactForm(sp=sp)
        elif "remove_contact" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    contact = Contact.objects.get(pk=key)
                    if contact.sp == sp:
                        contact.end_at = timezone.now()
                        contact.save()
                        sp.save_modified()
                        logger.info("Contact removed from {sp} by {user}"
                                    .format(sp=sp, user=request.user))
    contacts = Contact.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/contact.html", {'object_list': contacts,
                                               'form': form,
                                               'object': sp})
