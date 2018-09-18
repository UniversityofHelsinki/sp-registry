from cryptography.hazmat.primitives.serialization import Encoding

from django.forms import Form, Textarea, ValidationError
from django.forms.fields import CharField, BooleanField
from django.utils.translation import ugettext as _

from rr.models.certificate import Certificate, load_certificate


class CertificateForm(Form):
    """
    Form for importing certificates.
    Validating the certificate by trying to read it with cryptography library.
    """
    certificate = CharField(
            widget=Textarea,
            help_text=_("Certificate in PEM format, WITHOUT -----BEGIN CERTIFICATE----- and "
                        "-----END CERTIFICATE-----"))
    signing = BooleanField(
            required=False,
            help_text=_("Use this certificate for signing. If both signing and encryption are "
                        "left empty, certificate is used for both."))
    encryption = BooleanField(required=False,
                              help_text=_("Use this certificate for encryption"))

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(CertificateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        certificate = cleaned_data.get("certificate").strip()
        cert = load_certificate(certificate)
        if not cert:
            raise ValidationError(_("Unable to load certificate"))
        signing = cleaned_data.get("signing")
        encryption = cleaned_data.get("encryption")
        if not signing and not encryption:
            signing = True
            encryption = True
        if Certificate.objects.filter(
                sp=self.sp, certificate=cert.public_bytes(Encoding.PEM).decode("utf-8").replace(
                "-----BEGIN CERTIFICATE-----\n", "").replace("-----END CERTIFICATE-----\n", ""),
                signing=signing, encryption=encryption, end_at=None).exists():
            raise ValidationError(_("Certificate already exists"))
