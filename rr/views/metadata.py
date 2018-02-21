"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import ServiceProvider
from django.shortcuts import render
from django.http.response import Http404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
import logging
from rr.utils.metadata_generator import metadata_generator,\
    get_service_providers, metadata_generator_list
from rr.forms.metadata import MetadataForm, MetadataCommitForm
from lxml import etree
from rr.utils.metadata_parser import metadata_parser
from git import Repo, NoSuchPathError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from os.path import join
import hashlib
from datetime import datetime
from cgi import log

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


def last_commits(repo, n):
    """
    Returns list [time, commit_message] of last n commits to repo.
    """
    log = []
    log_ref = repo.head.reference.log()
    for x in range(1, n+1):
        if len(log_ref) < x:
            break
        log_entry = log_ref[-x]
        if log_entry:
            log.append([datetime.fromtimestamp(log_entry.time[0]), log_entry.message])
    return log


@login_required
def metadata_management(request):
    """
    View for managing metadata export repositorio

    **Context**

    ``form``
        Form for commit message.

    ``diff``
        uncommited changes.

    ``log``
        5 last commits.

    ``error``
        possible error/information message.

    **Template:**

    :template:`rr/repositorio_management.html`
    """
    error = None
    form = None
    if not request.user.is_superuser:
        raise PermissionDenied
    try:
        repo = Repo(settings.METADATA_GIT_REPOSITORIO)
    except:
        error_message = _("Repository not found.")
        return render(request, "error.html", {'error_message': error_message})
    origin = repo.remotes.origin
    diff = repo.git.diff('HEAD')
    # Load maximum 5 last commits
    log = last_commits(repo, 5)
    if repo.commit().hexsha != origin.fetch()[0].commit.hexsha:
        error = _("Remote repository not matching local, please fix manually.")
        return render(request, "rr/metadata_management.html", {'log': log,
                                                               'error': error})
    if request.method == "POST":
        form = MetadataCommitForm(request.POST)
        if form.is_valid() and diff:
            commit_message = form.cleaned_data['commit_message']
            form_hash = form.cleaned_data['diff_hash']
            # Check that file has not changed
            if form_hash == hashlib.md5(diff.encode('utf-8')).hexdigest():
                repo.index.add([settings.METADATA_FILENAME])
                repo.index.commit(commit_message)
                origin.push()
                # update last commits
                log = last_commits(repo, 5)
                if repo.commit().hexsha != origin.fetch()[0].commit.hexsha:
                    error = _("Pushing to remote did not work, please fix manually.")
                return render(request, "rr/metadata_management.html", {'log': log,
                                                                       'error': error})
            else:
                error = _("Metadata file has changed, please try again.")
    if not error:
        # Load service providers and write metadata to file
        serviceproviders = get_service_providers(validated=True, production=True)
        if serviceproviders:
                metadata = metadata_generator_list(serviceproviders, validated=True, privacypolicy=True)
                metadata_file = join(settings.METADATA_GIT_REPOSITORIO, settings.METADATA_FILENAME)
                with open(metadata_file, 'wb') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                    # Hack for correcting namespace definition by removing prefix.
                    f.write(etree.tostring(metadata, pretty_print=True, encoding='UTF-8').replace(b'xmlns:xmlns', b'xmlns'))
                    # update diff
                    diff = repo.git.diff('HEAD')
    diff_hash = hashlib.md5(diff.encode('utf-8')).hexdigest()
    form = MetadataCommitForm(diff_hash=diff_hash)
    return render(request, "rr/metadata_management.html", {'form': form,
                                                           'diff': diff,
                                                           'log': log,
                                                           'error': error})
