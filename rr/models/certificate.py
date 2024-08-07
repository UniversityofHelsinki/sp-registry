from datetime import timedelta

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import oid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from rr.models.serviceprovider import ServiceProvider


def certificate_validator(sp, certificate, signing, encryption, error):
    cert = load_certificate(certificate)
    if not cert:
        raise error(_("Unable to load certificate"))
    if not signing and not encryption:
        signing = True
        encryption = True
    if (
        sp
        and Certificate.objects.filter(
            sp=sp,
            certificate=cert.public_bytes(Encoding.PEM)
            .decode("utf-8")
            .replace("-----BEGIN CERTIFICATE-----\n", "")
            .replace("-----END CERTIFICATE-----\n", ""),
            signing=signing,
            encryption=encryption,
            end_at=None,
        ).exists()
    ):
        raise error(_("Certificate already exists"))


def load_certificate(certificate):
    if certificate.endswith("\n"):
        certificate = certificate + "-----END CERTIFICATE-----\n"
    else:
        certificate = certificate + "\n-----END CERTIFICATE-----\n"
    certificate = "-----BEGIN CERTIFICATE-----\n" + certificate
    try:
        cert = x509.load_pem_x509_certificate(certificate.encode("utf-8"), default_backend())
        return cert
    except ValueError as e:
        return False


class CertificateManager(models.Manager):
    def add_certificate(self, certificate, sp, signing=True, encryption=True, validate=False):
        """
        Manager for adding a certificate to database.
        """
        cert = load_certificate(certificate)
        if not cert:
            return False
        try:
            cn = cert.subject.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value
        except ValueError:
            cn = ""
        except IndexError:
            cn = ""
        try:
            issuer = cert.issuer.get_attributes_for_oid(oid.NameOID.COMMON_NAME)[0].value
        except ValueError:
            issuer = ""
        except IndexError:
            issuer = ""
        valid_from = cert.not_valid_before_utc
        valid_until = cert.not_valid_after_utc
        key_size = cert.public_key().key_size
        if validate:
            validated = timezone.now()
        else:
            validated = None
        try:
            created = self.create(
                sp=sp,
                cn=cn,
                issuer=issuer,
                valid_from=valid_from,
                valid_until=valid_until,
                key_size=key_size,
                certificate=cert.public_bytes(Encoding.PEM)
                .decode("utf-8")
                .replace("-----BEGIN CERTIFICATE-----\n", "")
                .replace("-----END CERTIFICATE-----\n", ""),
                signing=signing,
                encryption=encryption,
                validated=validated,
            )
        except ValueError as e:
            return None
        return created


class Certificate(models.Model):
    """
    Stores a single certificate, related to :model:`rr.ServiceProvider`

    SAML specific for saving certificate information.
    """

    sp = models.ForeignKey(ServiceProvider, related_name="certificates", on_delete=models.CASCADE)
    cn = models.CharField(max_length=255, blank=True, verbose_name=_("cn"))
    issuer = models.CharField(max_length=255, blank=True, verbose_name=_("Issuer cn"))
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid from"))
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid until"))
    key_size = models.SmallIntegerField(verbose_name=_("Key size"))
    certificate = models.TextField(verbose_name=_("Certificate"))
    signing = models.BooleanField(default=False, verbose_name=_("Use for signing"))
    encryption = models.BooleanField(default=False, verbose_name=_("Use for encryption"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Entry end time"))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_("Validated on"))

    objects = CertificateManager()

    def __str__(self):
        return "%s: Signing: %s, Encryption: %s" % (self.cn, self.signing, self.encryption)

    @property
    @extend_schema_field(OpenApiTypes.STR)
    def status(self):
        if self.end_at and not self.validated or self.end_at and self.validated > self.end_at:
            return _("removed")
        elif self.end_at:
            return _("pending removal")
        elif not self.validated:
            return _("pending validation")
        elif self.updated_at > self.validated + timedelta(minutes=1):
            return _("update pending validation")
        else:
            return _("validated")
