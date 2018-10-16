from django.db.models import Q
from django.core.validators import ValidationError
from django.forms import ModelForm, Form, CharField, BooleanField, PasswordInput
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.testuser import TestUser, TestUserData


class TestUserForm(ModelForm):

    userdata = BooleanField(required=False,
                            label=_("Generate attribute data for name and username based fields."))
    otherdata = BooleanField(required=False,
                             label=_("Generate random attribute data for other fields."))

    class Meta:
        model = TestUser
        fields = ['username', 'password', 'firstname', 'lastname', 'valid_for']
        widgets = {'password': PasswordInput()}

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        self.admin = kwargs.pop('admin', None)
        super(TestUserForm, self).__init__(*args, **kwargs)
        self.fields['valid_for'].queryset = ServiceProvider.objects.filter(
            Q(end_at=None, test=True, admins=self.admin) | Q(pk=self.sp.pk)).distinct()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        if TestUser.objects.filter(username=username, end_at=None).exists():
            raise ValidationError(_("Username already exists"))


class TestUserUpdateForm(ModelForm):

    class Meta:
        model = TestUser
        fields = ['password', 'firstname', 'lastname', 'valid_for']
        widgets = {'password': PasswordInput()}

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop('sp', None)
        self.admin = kwargs.pop('admin', None)
        super(TestUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['valid_for'].queryset = ServiceProvider.objects.filter(
            Q(end_at=None, test=True, admins=self.admin) | Q(pk=self.sp.pk) |
            Q(pk__in=self.instance.valid_for.all())).distinct()


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
            self.fields[field.attribute.friendlyname] = CharField(
                label=field.attribute.friendlyname, max_length=511, required=False)
            attribute_values = TestUserData.objects.filter(
                user=self.user, attribute=field.attribute).values_list('value')
            if attribute_values:
                self.fields[field.attribute.friendlyname].initial = ';'.join(
                    a[0] for a in attribute_values)
            else:
                self.fields[field.attribute.friendlyname].widget = TextInput(
                    attrs={'placeholder': ''})
