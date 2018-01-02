from django.db import models
from django.utils.translation import ugettext_lazy as _
from rr.models.serviceprovider import ServiceProvider
from django.utils import timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID


class CertificateManager(models.Manager):
    def add_certificate(self, certificate, sp):
            cert = x509.load_pem_x509_certificate(certificate.encode('utf-8'), default_backend())
            cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            valid_from = cert.not_valid_before
            valid_until = cert.not_valid_after
            key_size = cert.public_key().key_size
            try:
                self.create(sp=sp,
                            cn=cn,
                            issuer=issuer,
                            valid_from=valid_from,
                            valid_until=valid_until,
                            key_size=key_size,
                            certificate=certificate,
                            created=timezone.now())
            except ValueError:
                return False
            return True


class Certificate(models.Model):
    sp = models.ForeignKey(ServiceProvider)
    cn = models.CharField(max_length=255, blank=True, verbose_name=_('cn'))
    issuer = models.CharField(max_length=255, blank=True, verbose_name=_('Issuer cn'))
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name=_('Valid from'))
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_('Valid until'))
    key_size = models.SmallIntegerField(verbose_name=_('Key size'))
    certificate = models.TextField(verbose_name=_('Certificate'))
    created = models.DateTimeField(null=True, blank=True, verbose_name=_('Created at'))
    end_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Entry end time'))

    objects = CertificateManager()
