"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import ServiceProvider
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
import logging
from rr.utils.metadata_generator import metadata_generator
from rr.forms.metadata import MetadataForm
from lxml import etree
from rr.utils.metadata_parser import metadata_parser

logger = logging.getLogger(__name__)


@login_required
def metadata(request, pk):
    """
    Displays a metadata for :model:`rr.ServiceProvider`.

    **Context**

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    ``metadata``
        Metadata for a :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/metadata.html`
    """
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    if request.GET.get('validated', '') in ("false", "False"):
        validated = False
    else:
        validated = True
    metadata_sp = sp
    if validated and not sp.validated:
        metadata_sp = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
    if metadata_sp:
        metadata = metadata_generator(sp=metadata_sp, validated=validated)
    else:
        metadata = None
    return render(request, "rr/metadata.html", {'object': sp,
                                                'metadata': metadata,
                                                'validated': validated})


@login_required
def metadata_import(request):
    """
    Includes a form for adding new :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Text form for adding a certificate.

    **Template:**

    :template:`rr/metadata_import.html`
    """
    form = MetadataForm(user=request.user)
    errors = []
    sp = None
    if request.method == "POST":
        if "import_metadata" in request.POST:
            form = MetadataForm(request.POST, user=request.user)
            if form.is_valid():
                metadata = form.cleaned_data['metadata']
                disable_checks = request.POST.get('disable_checks', False)
                validate = request.POST.get('validate', False)
                parser = etree.XMLParser(ns_clean=True, remove_comments=True, remove_blank_text=True)
                entity = etree.fromstring(metadata, parser)
                sp, errors = metadata_parser(entity, overwrite=False, verbosity=2, validate=validate, disable_checks=disable_checks)
                if sp:
                    sp.admins.add(request.user)
                    form = None
                    logger.info("Metadata for SP %s imported by %s".format(sp=sp, user=request.user))
    return render(request, "rr/metadata_import.html", {'form': form,
                                                       'errors': errors,
                                                       'sp': sp})
