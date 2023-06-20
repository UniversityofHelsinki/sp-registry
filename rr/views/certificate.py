import binascii
import logging

from cryptography.hazmat.primitives import hashes
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _

from rr.forms.certificate import CertificateForm
from rr.models.certificate import Certificate, load_certificate
from rr.models.serviceprovider import ServiceProvider
from rr.utils.serviceprovider import get_service_provider

logger = logging.getLogger(__name__)


@login_required
def certificate_admin_list(request):
    """
    Displays a list of :model:`rr.Certificate`
    including old certificates and weak keys.

    Only available for super users.

    **Context**

    ``object_list``
        List of :model:`rr.Certificate`.

    **Template:**

    :template:`rr/attribute_admin_list.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    weak_certificates = Certificate.objects.filter(end_at=None, sp__end_at=None, key_size__lt=2048).order_by(
        "key_size"
    )
    expired_certificates = Certificate.objects.filter(
        end_at=None, sp__end_at=None, valid_until__lte=timezone.now()
    ).order_by("valid_until")
    return render(
        request,
        "rr/certificate_admin_list.html",
        {"weak_certificates": weak_certificates, "expired_certificates": expired_certificates},
    )


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
    sp = get_service_provider(pk, request.user, service_type=["saml"])
    form = CertificateForm(sp=sp)
    if request.method == "POST":
        if "add_cert" in request.POST:
            form = _add_certificate(request, sp)
        elif "remove_certificate" in request.POST:
            _remove_certificates(request, sp)
    certificates = Certificate.objects.filter(sp=sp, end_at=None)
    return render(request, "rr/certificate.html", {"object_list": certificates, "form": form, "object": sp})


def _add_certificate(request, sp):
    form = CertificateForm(request.POST, sp=sp)
    if form.is_valid():
        certificate = (
            form.cleaned_data["certificate"]
            .replace("-----BEGIN CERTIFICATE-----", "")
            .replace("-----END CERTIFICATE-----", "")
            .strip()
        )
        signing = form.cleaned_data["signing"]
        encryption = form.cleaned_data["encryption"]
        if not signing and not encryption:
            signing = True
            encryption = True
        if Certificate.objects.add_certificate(certificate, sp, signing=signing, encryption=encryption):
            form = CertificateForm(sp=sp)
            sp.save_modified()
            logger.info("Certificate added for {sp} by {user}".format(sp=sp, user=request.user))
            messages.add_message(request, messages.INFO, _("Certificate added."))
        else:
            messages.add_message(request, messages.WARNING, _("Could not add certificate."))
    return form


def _remove_certificates(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            cert = Certificate.objects.get(pk=key)
            if cert.sp == sp:
                cert.end_at = timezone.now()
                cert.save()
                sp.save_modified()
                logger.info("Certificate removed from {sp} by {user}".format(sp=sp, user=request.user))
                messages.add_message(request, messages.INFO, _("Certificate removed: ") + cert.cn)


@login_required
def certificate_info(request, pk):
    """
    Displays information of :model:`rr.Certificate` object.

    **Context**

    ``certificate``
        An instance of :model:`rr.Certificate`.

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    ``serial_number``
        Serial number of the certificate.

    ``fingerprint_sha256``
        SHA256 fingerprint of the certificate.

    ``fingerprint_sha1``
        SHA1 fingerprint of the certificate.

    ``fingerprint_md5``
        MD5 fingerprint of the certificate.

    **Template:**

    :template:`rr/certificate_info.html`
    """
    try:
        certificate = Certificate.objects.get(pk=pk, end_at=None)
    except Certificate.DoesNotExist:
        raise Http404(_("Certificate provided does not exist"))
    if (
        not request.user.is_superuser
        and not ServiceProvider.objects.filter(pk=certificate.sp.pk, admins=request.user, end_at=None).first()
    ):
        raise Http404(_("Certificate provided does not exist"))
    cert = load_certificate(certificate.certificate)
    serial_number = cert.serial_number
    fingerprint_sha256 = binascii.hexlify(cert.fingerprint(hashes.SHA256()))
    fingerprint_sha1 = binascii.hexlify(cert.fingerprint(hashes.SHA1()))
    fingerprint_md5 = binascii.hexlify(cert.fingerprint(hashes.MD5()))
    return render(
        request,
        "rr/certificate_info.html",
        {
            "certificate": certificate,
            "object": certificate.sp,
            "serial_number": serial_number,
            "fingerprint_sha256": fingerprint_sha256,
            "fingerprint_sha1": fingerprint_sha1,
            "fingerprint_md5": fingerprint_md5,
        },
    )
