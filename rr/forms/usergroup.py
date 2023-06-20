from django.core.validators import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from rr.models.usergroup import UserGroup


class UserGroupForm(ModelForm):
    class Meta:
        model = UserGroup
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp", None)
        super(UserGroupForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if UserGroup.objects.filter(sp=self.sp, name=name, end_at=None).exists():
            raise ValidationError(_("Group already added"))
