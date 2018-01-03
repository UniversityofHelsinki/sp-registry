from rr.models.serviceprovider import ServiceProvider
from rr.models.certificate import Certificate
from rr.forms.certificate import CertificateForm
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def certificate_list(request, pk):
    try:
        sp = ServiceProvider.objects.get(pk=pk, admins=request.user)
    except ServiceProvider.DoesNotExist:
        raise Http404("Service proviced does not exist")
    if request.method == "POST":
        if "add_cert" in request.POST:
            form = CertificateForm(request.POST)
            if form.is_valid():
                certificate = form.cleaned_data['certificate']
                signing = form.cleaned_data['signing']
                encryption = form.cleaned_data['encryption']
                if Certificate.objects.add_certificate(certificate, sp, signing=signing, encryption=encryption):
                    form = CertificateForm()
        else:
            form = CertificateForm()
            # For certificate removal, check for the first POST item after csrf
            if (list(request.POST.dict().values())[1]) == "Remove":
                cert_id = list(request.POST.dict().keys())[1]
                cert = Certificate.objects.get(pk=cert_id)
                if cert.sp == sp:
                    cert.end_at = timezone.now()
                    cert.save()
    else:
        form = CertificateForm()
    certificates = Certificate.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/certificate.html", {'object_list': certificates,
                                                   'form': form,
                                                   'object': sp})
