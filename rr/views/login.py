from django.shortcuts import render
from django.views import View
from django.contrib.auth import login
from auth.shibboleth import ShibbolethBackend
from django.utils.translation import ugettext as _
from django.http.response import HttpResponseRedirect
from django.conf import settings
from django.urls.base import reverse
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class ShibbolethLoginView(View):
    """
    LoginView to authenticate user against Shibboleth
    """
    def get(self, request, *args, **kwargs):
        redirect_to = request.GET.get('next', '/')
        user = ShibbolethBackend.authenticate(self, request)
        if user:
            if user.is_active:
                login(request, user, backend='auth.shibboleth.ShibbolethBackend')
                # Save login method to session
                request.session['LOGIN_METHOD'] = "Shibboleth"
                logger.info("User {user} logged in".format(user=user))
                if redirect_to == request.path:
                    error_message = _("Redirection loop for authenticated user detected. Check that your LOGIN_REDIRECT_URL doesn't point to a login page.")
                    logger.error("Redirection loop detected")
                    return render(request, "error.html", {'error_message': error_message})
                return HttpResponseRedirect(redirect_to)
            else:
                info_message = _("Your user account has been deactivated.")
                logger.warning("User {user} with deactivated account tried to log in".format(user=user))
                contact = settings.DEFAULT_CONTACT_EMAIL
                return render(request, "info.html", {'info_message': info_message,
                                                     'contact': contact})
        else:
            logger.debug("Failed Shibboleth login")
        return HttpResponseRedirect(reverse('serviceprovider-list'))


def logout_redirect(request):
    """
    Redirect to Shibboleth logout url for SLO, if login method is Shibboleth
    and url is configured. Otherwise use local logout.
    """
    login_method = request.session.get('LOGIN_METHOD', None)
    if login_method == "Shibboleth" and settings.SHIBBOLETH_LOGOUT_URL:
        return HttpResponseRedirect(settings.SHIBBOLETH_LOGOUT_URL)
    else:
        return HttpResponseRedirect(reverse('logout-local'))


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):

    ip = request.META.get('REMOTE_ADDR')

    logger.info('login user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):

    ip = request.META.get('REMOTE_ADDR')

    logger.info('logout user: {user} via ip: {ip}'.format(
        user=user,
        ip=ip
    ))
