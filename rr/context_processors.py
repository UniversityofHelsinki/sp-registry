from django.conf import settings

def saml_login_url(request):
    return {'SAML_LOGIN_URL': settings.SAML_LOGIN_URL}
