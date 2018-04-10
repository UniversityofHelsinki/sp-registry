from django.forms import ModelForm, Form, CharField, BooleanField, PasswordInput
from rr.models.serviceprovider import SPAttribute
from rr.models.testuser import TestUser, TestUserData
from django.core.validators import ValidationError
from django.utils.translation import ugettext as _
from django.forms.widgets import TextInput


class TestUserForm(ModelForm):

    userdata = BooleanField(required=False, label=_("Generate attribute data for name and username based fields."))
    otherdata = BooleanField(required=False, label=_("Generate random attribute data for other fields."))

    class Meta:
        model = TestUser
        fields = ['username', 'password', 'firstname', 'lastname']
        widgets = {'password': PasswordInput()}

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        super(TestUserForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        if TestUser.objects.filter(sp=self.sp, username=username, end_at=None).exists():
            raise ValidationError(_("Username already exists"))


class PasswordResetForm(Form):

    password = CharField(widget=PasswordInput)


class TestUserDataForm(Form):
    """
    Generates form including all SP attributes and allows giving values for those attributes
    Pass ServiceProvider object as argument
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TestUserDataForm, self).__init__(*args, **kwargs)
        attributes = SPAttribute.objects.filter(sp=self.user.sp, end_at=None)
        for field in attributes:
            self.fields[field.attribute.friendlyname] = CharField(label=field.attribute.friendlyname, max_length=511, required=False)
            attribute = TestUserData.objects.filter(user=self.user, attribute=field.attribute).first()
            if attribute:
                self.fields[field.attribute.friendlyname].initial = attribute.value
            else:
                self.fields[field.attribute.friendlyname].widget = TextInput(attrs={'placeholder': ''})
