""""
Custom handlers for status pages
"""
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)


def bad_request(request):
    logger.warning("Bad request")
    values_for_template = {}
    return render(request, 'handlers/400.html', values_for_template, status=400)


def permission_denied(request):
    values_for_template = {}
    return render(request, 'handlers/403.html', values_for_template, status=403)


def page_not_found(request):
    values_for_template = {}
    return render(request, 'handlers/404.html', values_for_template, status=404)


def server_error(request):
    logger.error("Internal server error")
    values_for_template = {}
    return render(request, 'handlers/500.html', values_for_template, status=500)
