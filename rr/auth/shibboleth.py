from django.contrib.auth.models import User
import re
from django.conf import settings
from django.contrib.auth import login


class ShibbolethBackend:
    """
    Backend for Shibboleth authentication.
    If Shibboleth EPPN is found, signs user in, creating a new user if nesessary.
    """
    def authenticate(self, request):
        username = request.META.get(settings.SAML_ATTR_EPPN, '')
        first_name = request.META.get(settings.SAML_ATTR_FIRST_NAME, '')
        last_name = request.META.get(settings.SAML_ATTR_LAST_NAME, '')
        email = request.META.get(settings.SAML_ATTR_EMAIL, '')

        if username and re.match("[^@]+@[^@]+\.[^@]+", username):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user with unusable password
                user = User(username=username,
                            password=User.objects.make_random_password(),
                            first_name=first_name,
                            last_name=last_name,
                            email=email)
                user.set_unusable_password = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
