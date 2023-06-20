from django.core.validators import ValidationError
from django.forms import ModelForm

from rr.models.redirecturi import RedirectUri, redirecturi_validator


class RedirectUriForm(ModelForm):
    class Meta:
        model = RedirectUri
        fields = ["uri"]

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp", None)
        super(RedirectUriForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        uri = cleaned_data.get("uri")
        if uri:
            redirecturi_validator(self.sp, uri, ValidationError)
