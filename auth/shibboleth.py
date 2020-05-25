import logging
import re

from django.conf import settings
from django.contrib.auth.models import Group, User

logger = logging.getLogger(__name__)


def update_groups(user, groups):
    """
    Set users groups based on SAML_ATTR_GROUPS parameter

    user: User object
    groups: string of group names, separated by semicolon
    """
    login_groups = Group.objects.filter(name__in=groups.split(';'))
    user_groups = user.groups.all()
    removed = list(set(user_groups) - set(login_groups))
    added = list(set(login_groups) - set(user_groups))
    for group in removed:
        user.groups.remove(group)
    for group in added:
        user.groups.add(group)


class ShibbolethBackend:
    """
    Backend for Shibboleth authentication.
    If Shibboleth EPPN is found, signs user in,
    creating a new user if necessary.
    """
    def authenticate(self, request):
        username = request.META.get(settings.SAML_ATTR_EPPN, '')
        first_name = request.META.get(
            settings.SAML_ATTR_FIRST_NAME, '').encode('latin1').decode('utf-8', 'ignore')
        last_name = request.META.get(
            settings.SAML_ATTR_LAST_NAME, '').encode('latin1').decode('utf-8', 'ignore')
        email = request.META.get(settings.SAML_ATTR_EMAIL, '')
        affiliations = request.META.get(settings.SAML_ATTR_AFFILIATION, '')
        groups = request.META.get(settings.SAML_ATTR_GROUPS, '')

        if username and re.match("[^@]+@[^@]+\.[^@]+", username):
            try:
                user = User.objects.get(username=username)
                update_groups(user, groups)
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    logger.debug("Updated user information for user %s", username)
            except User.DoesNotExist:
                # Create a new user with unusable password
                logger.info("Created a new user: %s", username)
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
                update_groups(user, groups)
            return user
        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
