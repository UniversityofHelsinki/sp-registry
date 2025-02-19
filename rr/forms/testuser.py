import re

from django.core.validators import ValidationError
from django.db.models import Q
from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    Form,
    ModelForm,
    PasswordInput,
)
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from rr.models.attribute import Attribute
from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.testuser import TestUser, TestUserData


def hostname_validator(hostname):
    if len(hostname) > 253:
        return False
    parts = hostname.split(".")
    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(part) for part in parts)


class TestUserForm(ModelForm):
    userdata = BooleanField(required=False, label=_("Generate attribute data for name and username based fields."))
    otherdata = BooleanField(required=False, label=_("Generate random attribute data for other fields."))
    scope = CharField(
        required=False,
        max_length=253,
        label=_("Scope"),
        help_text=_("Scope for scoped attributes. Default is 'example.org'."),
    )

    CHOICES = ((1, _("1")), (5, _("5")), (10, _("10")), (50, _("50")))
    number_of_users = ChoiceField(
        required=False,
        choices=CHOICES,
        label=_("Number of users"),
        help_text=_("Create X users. Username and password will be appended with <number>"),
    )

    class Meta:
        model = TestUser
        fields = ["username", "password", "firstname", "lastname", "valid_for"]
        widgets = {"password": PasswordInput()}

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp", None)
        self.admin = kwargs.pop("admin", None)
        super(TestUserForm, self).__init__(*args, **kwargs)
        self.fields["valid_for"].queryset = ServiceProvider.objects.filter(
            Q(end_at=None, test=True, admins=self.admin) | Q(pk=self.sp.pk)
        ).distinct()

    def clean_scope(self):
        data = self.cleaned_data["scope"]
        if data and not hostname_validator(data):
            raise ValidationError(_("Scope must be a valid hostname"))
        return data

    def clean(self):
        cleaned_data = super().clean()
        number_of_users = cleaned_data.get("number_of_users")
        try:
            int(number_of_users)
        except ValueError:
            raise ValidationError(_("Number of users must be integer"))
        username = cleaned_data.get("username")
        if TestUser.objects.filter(username=username, end_at=None).exists():
            raise ValidationError(_("Username already exists"))


class TestUserUpdateForm(ModelForm):
    class Meta:
        model = TestUser
        fields = ["password", "firstname", "lastname", "valid_for"]
        widgets = {"password": PasswordInput()}

    def __init__(self, *args, **kwargs):
        self.sp = kwargs.pop("sp", None)
        self.admin = kwargs.pop("admin", None)
        super(TestUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields["password"].required = False
        self.fields["valid_for"].queryset = ServiceProvider.objects.filter(
            Q(end_at=None, test=True, admins=self.admin) | Q(pk=self.sp.pk) | Q(pk__in=self.instance.valid_for.all())
        ).distinct()


class TestUserDataForm(Form):
    """
    Generates form including all SP attributes and allows giving values for those attributes
    Pass ServiceProvider object as argument
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(TestUserDataForm, self).__init__(*args, **kwargs)
        attributes = SPAttribute.objects.filter(sp=self.user.sp, end_at=None)
        for field in attributes:
            self.fields[field.attribute.friendlyname] = CharField(
                label=field.attribute.friendlyname, max_length=511, required=False
            )
            attribute_values = TestUserData.objects.filter(user=self.user, attribute=field.attribute).values_list(
                "value"
            )
            if attribute_values:
                self.fields[field.attribute.friendlyname].initial = ";".join(a[0] for a in attribute_values)
            else:
                self.fields[field.attribute.friendlyname].widget = TextInput(attrs={"placeholder": ""})

    def clean(self):
        cleaned_data = super().clean()
        for field in cleaned_data:
            data = cleaned_data.get(field)
            values = data.split(";")
            attribute = Attribute.objects.filter(friendlyname=field).first()
            if attribute.scoped:
                scoped_test = re.compile(r"^[^@\s]+@[^@\s]+$")
                for value in values:
                    if not scoped_test.match(value):
                        raise ValidationError({field: [_("Value must be scoped")]})
