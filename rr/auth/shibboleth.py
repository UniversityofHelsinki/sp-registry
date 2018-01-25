from django.contrib.auth.models import User
import re
from django.conf import settings


class ShibbolethBackend:
    """
    Backend for Shibboleth authentication.
    If Shibboleth EPPN is found, signs user in, creating a new user if nesessary.
    """
    def authenticate(self, request):
        username = request.META.get(settings.SAML_ATTR_EPPN, '')
        first_name = request.META.get(settings.SAML_ATTR_FIRST_NAME, '').encode('latin1').decode('utf-8', 'ignore')
        last_name = request.META.get(settings.SAML_ATTR_LAST_NAME, '').encode('latin1').decode('utf-8', 'ignore')
        email = request.META.get(settings.SAML_ATTR_EMAIL, '')
        affiliations = request.META.get(settings.SAML_ATTR_AFFILIATION, '')

        if username and re.match("[^@]+@[^@]+\.[^@]+", username):
            try:
                user = User.objects.get(username=username)
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
            except User.DoesNotExist:
                # Create a new user with unusable password
                if "faculty" in affiliations or "staff" in affiliations:
                    active = True
                else:
                    active = False
                user = User(username=username,
                            password=User.objects.make_random_password(),
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            is_active=active)
                user.set_unusable_password = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
