from django.contrib.auth.models import User
import re


class ShibbolethAuthModelBackend(object):
    """
    Model Backend for Shibboleth authentication
    """
    def authenticate(self, request):
        """
        returns user object with user_id
        creates user if it's not found
        Keywords:
            user_id: user to be authenticated
        """
        username = request.META.get('shib_eppn', 'None')
        first_name = request.META.get('shib_first_name', 'None')
        last_name = request.META.get('shib_last_name', 'None')
        email = request.META.get('shib_email', 'None')

        if re.match("[^@]+@[^@]+\.[^@]+", username):
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
