"""
Custom handlers for status pages
"""

import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def bad_request(request, exception):
    logger.warning("Bad request: " + exception)
    values_for_template = {}
    return render(request, "handlers/400.html", values_for_template, status=400)


def bad_request_blank(request, exception):
    logger.warning("Bad request: " + exception)
    values_for_template = {}
    return render(request, "handlers/400_blank.html", values_for_template, status=400)


def permission_denied(request, exception):
    values_for_template = {}
    return render(request, "handlers/403.html", values_for_template, status=403)


def permission_denied_blank(request, exception):
    values_for_template = {}
    return render(request, "handlers/403_blank.html", values_for_template, status=403)


def page_not_found(request, exception):
    values_for_template = {}
    return render(request, "handlers/404.html", values_for_template, status=404)


def page_not_found_blank(request, exception):
    values_for_template = {}
    return render(request, "handlers/404_blank.html", values_for_template, status=404)


def server_error(request):
    logger.error("Internal server error")
    values_for_template = {}
    return render(request, "handlers/500.html", values_for_template, status=500)


def server_error_blank(request):
    logger.error("Internal server error")
    values_for_template = {}
    return render(request, "handlers/500_blank.html", values_for_template, status=500)
