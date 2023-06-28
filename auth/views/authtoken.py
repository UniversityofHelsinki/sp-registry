import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


@login_required
def authtoken(request):
    """
    View for creating, resetting and removing auth tokens.
    """
    try:
        token = Token.objects.get(user=request.user)
    except Token.DoesNotExist:
        token = None
    if request.method == "POST":
        if "token_create" in request.POST:
            token, created = Token.objects.get_or_create(user=request.user)
        elif "token_reset" in request.POST:
            if token:
                token.delete()
            token, created = Token.objects.get_or_create(user=request.user)
        elif "token_remove" in request.POST:
            if token:
                token.delete()
            token = None
    return render(request, "authtoken.html", {"token": token})
