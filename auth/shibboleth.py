import logging
import re

from django.conf import settings
from django.contrib.auth.models import Group, User

logger = logging.getLogger(__name__)


def get_activation(affiliations, groups):
    """
    Get default active status based on users affiliations and groups

    affiliations: list of affiliations
    groups: list of group names
    """
    if hasattr(settings, "AUTO_ACTIVATE_AFFILIATIONS") and isinstance(settings.AUTO_ACTIVATE_AFFILIATIONS, list):
        auto_activate_affiliations = settings.AUTO_ACTIVATE_AFFILIATIONS
    else:
        auto_activate_affiliations = []
    if hasattr(settings, "AUTO_ACTIVATE_GROUPS") and isinstance(settings.AUTO_ACTIVATE_GROUPS, list):
        auto_activate_groups = settings.AUTO_ACTIVATE_GROUPS
    else:
        auto_activate_groups = []
    if any(ele in auto_activate_affiliations for ele in affiliations):
        return True
    elif any(ele in auto_activate_groups for ele in groups):
        return True
    return False


def update_groups(user, groups):
    """
    Set users groups based on SAML_ATTR_GROUPS parameter

    user: User object
    groups: list of group names
    """
    login_groups = Group.objects.filter(name__in=groups)
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
        username = request.META.get(settings.SAML_ATTR_EPPN, "")
        first_name = request.META.get(settings.SAML_ATTR_FIRST_NAME, "").encode("latin1").decode("utf-8", "ignore")
        last_name = request.META.get(settings.SAML_ATTR_LAST_NAME, "").encode("latin1").decode("utf-8", "ignore")
        email = request.META.get(settings.SAML_ATTR_EMAIL, "")
        affiliations = request.META.get(settings.SAML_ATTR_AFFILIATION, "").split(";")
        groups = request.META.get(settings.SAML_ATTR_GROUPS, "").split(";")
        if username and re.match("[^@]+@[^@]+\.[^@]+", username):
            try:
                user = User.objects.get(username=username)
                update_groups(user, groups)
                if not user.is_active and get_activation(affiliations, groups):
                    user.is_active = True
                    logger.debug("Activated user %s", username)
                    user.save()
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    logger.debug("Updated user information for user %s", username)
            except User.DoesNotExist:
                # Create a new user with unusable password
                logger.info("Created a new user: %s", username)
                active = get_activation(affiliations, groups)
                user = User(
                    username=username,
                    password=User.objects.make_random_password(),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_active=active,
                )
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
