from django.shortcuts import render
from django.views import View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from rr.auth.shibboleth import ShibbolethBackend
from django.utils.translation import ugettext_lazy as _


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
            else:
                info_message = _("Your user account has been deactivated.")
                return render(request, "info.html", {'info_message': info_message})
        return super().get(request, *args, **kwargs)
