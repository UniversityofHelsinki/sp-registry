from django.shortcuts import render


def sp_error(request):
    """
    Parses error URL parameters and displays SP errors.

    **Template:**

    :template:`rr/sp_error.html`
    """
    error_type = request.GET.get('errorType')
    error_time = request.GET.get('now')
    error_text = request.GET.get('errorText')
    error_status = request.GET.get('statusCode')
    error_status2 = request.GET.get('statusCode2')
    if (error_type and error_status2 and error_type.strip() == "opensaml::FatalProfileException" and
            error_status2.strip() == "urn:oasis:names:tc:SAML:2.0:status:NoAuthnContext"):
        return render(request, "error/mfa.html")
    return render(request, "error/sp.html", {'error_type': error_type,
                                             'error_time': error_time,
                                             'error_text': error_text,
                                             'error_status': error_status,
                                             'error_status2': error_status2})
