from rr.models.serviceprovider import ServiceProvider
from rr.models.contact import Contact
from rr.forms.contact import ContactForm
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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
            sp = ServiceProvider.objects.get(pk=pk)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service proviced does not exist")
    if request.method == "POST":
        if "add_contact" in request.POST:
            form = ContactForm(request.POST)
            if form.is_valid():
                contact_type = form.cleaned_data['type']
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                email = form.cleaned_data['email']
                Contact.objects.create(sp=sp,
                                       type=contact_type,
                                       firstname=firstname,
                                       lastname=lastname,
                                       email=email,
                                       created=timezone.now())
        else:
            form = ContactForm()
            # For certificate removal, check for the first POST item after csrf
            if (list(request.POST.dict().values())[1]) == "Remove":
                contact_id = list(request.POST.dict().keys())[1]
                contact = Contact.objects.get(pk=contact_id)
                if contact.sp == sp:
                    contact.end_at = timezone.now()
                    contact.save()
    else:
        form = ContactForm()
    contacts = Contact.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/contact.html", {'object_list': contacts,
                                               'form': form,
                                               'object': sp})
