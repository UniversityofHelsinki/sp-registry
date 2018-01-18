from django.shortcuts import render
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from rr.auth.shibboleth import ShibbolethBackend
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.conf import settings


class FrontPage(View):
    template_name = 'rr/front_page.html'

    def get(self, request):
        return render(request, self.template_name)


class CustomLoginView(LoginView):

    def get(self, request, *args, **kwargs):
        user = ShibbolethBackend.authenticate(self, request)
        if user:
            if user.is_active:
                login(request, user)
                redirect_to = self.get_success_url()
                if redirect_to == self.request.path:
                    error_message = _("Redirection loop for authenticated user detected. Check that your LOGIN_REDIRECT_URL doesn't point to a login page.")
                    return render(request, "error.html", {'error_message': error_message})
                return HttpResponseRedirect(redirect_to)
            else:
                info_message = _("Your user account has been deactivated.")
                contact = settings.DEFAULT_CONTACT_EMAIL
                return render(request, "info.html", {'info_message': info_message,
                                                     'contact': contact})
        return super().get(request, *args, **kwargs)
