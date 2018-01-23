from rr.models.serviceprovider import ServiceProvider
from rr.models.certificate import Certificate
from rr.forms.certificate import CertificateForm
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def certificate_list(request, pk):
    """
    Displays a list of :model:`rr.Certificate` linked to
    :model:`rr.ServiceProvider`.

    Includes a form for adding :model:`rr.Certificate` to
    :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Certificate`.

    ``form``
        Text form for adding a certificate.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/certificate.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service provider does not exist")
    form = CertificateForm(sp=sp)
    if request.method == "POST":
        if "add_cert" in request.POST:
            form = CertificateForm(request.POST, sp=sp)
            if form.is_valid():
                certificate = form.cleaned_data['certificate']
                signing = form.cleaned_data['signing']
                encryption = form.cleaned_data['encryption']
                if not signing and not encryption:
                    signing = True
                    encryption = True
                if Certificate.objects.add_certificate(certificate, sp, signing=signing, encryption=encryption):
                    form = CertificateForm(sp=sp)
                    sp.modified = True
                    sp.save()
        elif "remove_certificate" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    cert = Certificate.objects.get(pk=key)
                    if cert.sp == sp:
                        cert.end_at = timezone.now()
                        cert.save()
                        sp.modified = True
                        sp.save()
    certificates = Certificate.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/certificate.html", {'object_list': certificates,
                                                   'form': form,
                                                   'object': sp})
