from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider
from django.utils import timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID
import pytz


def load_certificate(certificate):
    if certificate.endswith("\n"):
        certificate = certificate + "-----END CERTIFICATE-----\n"
    else:
        certificate = certificate + "\n-----END CERTIFICATE-----\n"
    certificate = "-----BEGIN CERTIFICATE-----\n" + certificate
    try:
        cert = x509.load_pem_x509_certificate(certificate.encode('utf-8'), default_backend())
        return cert
    except ValueError:
        return False


class CertificateManager(models.Manager):
    def add_certificate(self, certificate, sp, signing=None, encryption=None):
        """
        Manager for adding a certificate to database.
        """
        cert = load_certificate(certificate)
        try:
            cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except ValueError:
            cn = ""
        except IndexError:
            cn = ""
        try:
            issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except ValueError:
            issuer = ""
        except IndexError:
            issuer = ""
        valid_from = cert.not_valid_before
        valid_until = cert.not_valid_after
        key_size = cert.public_key().key_size
        try:
            self.create(sp=sp,
                        cn=cn,
                        issuer=issuer,
                        valid_from=pytz.utc.localize(valid_from),
                        valid_until=pytz.utc.localize(valid_until),
                        key_size=key_size,
                        certificate=cert.public_bytes(Encoding.PEM).decode("utf-8").replace(
                            "-----BEGIN CERTIFICATE-----\n", "").replace("-----END CERTIFICATE-----\n", ""),
                        signing=signing,
                        encryption=encryption,
                        validated=timezone.now())
        except ValueError:
            return False
        return True


class Certificate(models.Model):
    """
    Stores a single certificate, related to :model:`rr.ServiceProvider`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    cn = models.CharField(max_length=255, blank=True, verbose_name=_('cn'))
    issuer = models.CharField(max_length=255, blank=True, verbose_name=_('Issuer cn'))
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name=_('Valid from'))
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_('Valid until'))
    key_size = models.SmallIntegerField(verbose_name=_('Key size'))
    certificate = models.TextField(verbose_name=_('Certificate'))
    signing = models.BooleanField(default=False, verbose_name=_('Use for signing'))
    encryption = models.BooleanField(default=False, verbose_name=_('Use for encryption'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))
    validated = models.DateTimeField(null=True, blank=True, verbose_name=_('Validated on'))

    objects = CertificateManager()
