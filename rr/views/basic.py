from django.shortcuts import render
from django.views import View
from django.contrib.auth import login
from rr.auth.shibboleth import ShibbolethBackend
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.conf import settings
from django.urls.base import reverse
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
                login(request, user, backend='rr.auth.shibboleth.ShibbolethBackend')
                logger.info("User %s logged in", user)
                if redirect_to == request.path:
                    error_message = _("Redirection loop for authenticated user detected. Check that your LOGIN_REDIRECT_URL doesn't point to a login page.")
                    logger.error("Redirection loop detected")
                    return render(request, "error.html", {'error_message': error_message})
                return HttpResponseRedirect(redirect_to)
            else:
                info_message = _("Your user account has been deactivated.")
                logger.warning("User %s with deactivated account tried to log in", user)
                contact = settings.DEFAULT_CONTACT_EMAIL
                return render(request, "info.html", {'info_message': info_message,
                                                     'contact': contact})
        else:
            logger.debug("Failed shibboleth login")
        return HttpResponseRedirect(reverse('serviceprovider-list'))
