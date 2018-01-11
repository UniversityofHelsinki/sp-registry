from django.shortcuts import redirect
from django.contrib.auth import authenticate, logout
from django.conf import settings


def login(request):
    """
    Authenticates the user.

    Redirects to SAML_LOGIN_URL if authentication information is not found.

    If success, redirects back to page authentication was request from.
    """
    user = authenticate(request)
    redirect_to = request.GET.get('next', '/')
    if not user:
        return redirect(settings.SAML_LOGIN_URL + redirect_to)
    else:
        return redirect(redirect_to)


def logout(request):
    """
    Logs out user and redirects to SAML logout URL.
    """
    logout(request)
    logout_url = request.META.get(settings.SAML_LOGOUT_URL, '/')
    return redirect(logout_url)
