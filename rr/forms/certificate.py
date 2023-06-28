from django.forms import Form, Textarea, ValidationError
from django.forms.fields import BooleanField, CharField
from django.utils.translation import gettext_lazy as _

from rr.models.certificate import certificate_validator


class CertificateForm(Form):
    """
    Form for importing certificates.
    Validating the certificate by trying to read it with cryptography library.
    """

    certificate = CharField(
        widget=Textarea,
        help_text=_("Certificate in PEM format, WITHOUT -----BEGIN CERTIFICATE----- and -----END CERTIFICATE-----"),
    )
    signing = BooleanField(
        required=False,
        help_text=_(
            "Use this certificate for signing. If both signing and encryption are "
            "left empty, certificate is used for both."
        ),
    )
    encryption = BooleanField(required=False, help_text=_("Use this certificate for encryption"))

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp", None)
        super(CertificateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        certificate = (
            cleaned_data.get("certificate")
            .replace("-----BEGIN CERTIFICATE-----", "")
            .replace("-----END CERTIFICATE-----", "")
            .strip()
        )
        signing = cleaned_data.get("signing")
        encryption = cleaned_data.get("encryption")
        certificate_validator(self.sp, certificate, signing, encryption, ValidationError)
