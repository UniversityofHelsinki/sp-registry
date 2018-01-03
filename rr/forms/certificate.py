from django.forms import Form, Textarea, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class CertificateForm(Form):
    certificate = CharField(widget=Textarea,
                            help_text=_("Certificate in PEM format, including -----BEGIN CERTIFICATE----- and -----END CERTIFICATE-----"))
    signing = BooleanField(required=False, help_text=_("Use this certificate for signing. If both signing and encryption are left empty, certificate is used for both."))
    encryption = BooleanField(required=False, help_text=_("Use this certificate for encryption"))

    def clean_certificate(self):
        cert = self.cleaned_data['certificate']
        try:
            x509.load_pem_x509_certificate(cert.encode('utf-8'), default_backend())
        except ValueError as e:
            raise ValidationError(e)
        return cert
