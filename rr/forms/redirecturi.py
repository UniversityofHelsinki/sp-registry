from django.core.validators import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from rr.models.redirecturi import RedirectUri


class RedirectUriForm(ModelForm):
    class Meta:
        model = RedirectUri
        fields = ['uri']

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(RedirectUriForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        uri = cleaned_data.get("uri")
        if uri:
            if ':' not in uri or uri.startswith(':') or uri.endswith(':'):
                raise ValidationError(_('Enter a valid URI.'))
            if RedirectUri.objects.filter(sp=self.sp, uri=uri, end_at=None).exists():
                raise ValidationError(_('URI already exists'))
            if self.sp.application_type == 'web' and not uri.startswith('https://'):
                raise ValidationError(_('Web application URIs must begin with https: scheme'))
            if '#' in uri:
                raise ValidationError(_('URIs must not contain fragments'))
            if (self.sp.application_type == 'native' and uri.startswith('http') and
                    not uri.startswith('http://localhost')):
                raise ValidationError(_('Native applications must use custom URI schemes or http: scheme with '
                                        'localhost as the hostname.'))
