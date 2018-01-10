from django.shortcuts import redirect
from django.contrib.auth import authenticate, logout
from django.conf import settings


def login(request):
    user = authenticate(request)
    redirect_to = request.GET.get('next', '/')
    if not user:
        return redirect(settings.SAML_LOGIN_URL + redirect_to)
    else:
        return redirect(redirect_to)


def logout(request):
    logout(request)
    return redirect('/')
