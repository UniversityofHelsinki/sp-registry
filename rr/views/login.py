import logging

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.views import LogoutView
from django.dispatch import receiver
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from auth.shibboleth import ShibbolethBackend

logger = logging.getLogger(__name__)


class ShibbolethLoginView(View):
    """
    LoginView to authenticate user against Shibboleth
    """

    def get(self, request, *args, **kwargs):
        redirect_to = request.GET.get("next", "/")
        user = ShibbolethBackend.authenticate(self, request)
        if user:
            if user.is_active:
                login(request, user, backend="auth.shibboleth.ShibbolethBackend")
                # Save login method to session
                request.session["LOGIN_METHOD"] = "Shibboleth"
                logger.info("User {user} logged in".format(user=user))
                if redirect_to == request.path:
                    error_message = _(
                        "Redirection loop for authenticated user detected. "
                        "Check that your LOGIN_REDIRECT_URL doesn't point to "
                        "a login page."
                    )
                    logger.error("Redirection loop detected")
                    return render(request, "error.html", {"error_message": error_message})
                return HttpResponseRedirect(redirect_to)
            else:
                info_message = _("Your user account has been deactivated.")
                logger.warning("User {user} with deactivated account tried to log in".format(user=user))
                contact = settings.DEFAULT_CONTACT_EMAIL
                return render(request, "info.html", {"info_message": info_message, "contact": contact})
        else:
            logger.debug("Failed Shibboleth login")
        return HttpResponseRedirect(reverse("serviceprovider-list"))


@method_decorator([csrf_protect, never_cache], name="post")
class LocalLogoutView(LogoutView):
    """
    Custom logout view to redirect to the correct page.
    """

    template_name = "registration/logout.html"
    http_method_names = ["get", "head", "post", "options"]

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """
        Set next page to the correct url.

        If it's from a Shibboleth SP front-channel notification, return it to return url.
        """
        if "action" in request.GET and request.GET.get("action") == "logout" and "return" in request.GET:
            self.next_page = request.GET.get("return")
        login_method = request.session.get("LOGIN_METHOD", None)
        if login_method == "Shibboleth" and settings.SHIBBOLETH_LOGOUT_URL:
            self.next_page = settings.SHIBBOLETH_LOGOUT_URL
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Redirect get to post. Support to get logouts was removed in Django 5.0, but it is required
        for Shibboleth front-channel logout notifications.
        """
        return super().post(request, *args, **kwargs)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR")

    logger.info("login user: {user} via ip: {ip}".format(user=user, ip=ip))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get("REMOTE_ADDR")

    logger.info("logout user: {user} via ip: {ip}".format(user=user, ip=ip))
