"""
Functions for genereating metadata of service providers
"""

import hashlib
import logging
import os
from datetime import datetime
from os.path import join
from glob import glob

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError, GitCommandError
from lxml import etree

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _

from rr.forms.metadata import MetadataForm, MetadataCommitForm
from rr.models.serviceprovider import ServiceProvider
from rr.utils.metadata_generator import metadata_generator
from rr.utils.metadata_generator import metadata_generator_list
from rr.utils.metadata_parser import metadata_parser
from rr.utils.ldap_metadata_generator import ldap_metadata_generator_list

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
            sp = ServiceProvider.objects.get(pk=pk, end_at=None, service_type="saml")
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None,
                                             service_type="saml")
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    if request.GET.get('validated', '') in ("false", "False"):
        validated = False
    else:
        validated = True
    metadata_sp = sp
    metadata = None
    if metadata_sp:
        tree = metadata_generator(sp=metadata_sp, validated=validated)
        if tree is not None:
            metadata = etree.tostring(tree, pretty_print=True,
                                      encoding='UTF-8').replace(b'xmlns:xmlns', b'xmlns')
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
                metadata = form.cleaned_data['metadata'].encode('utf-8')
                disable_checks = request.POST.get('disable_checks', False)
                validate = request.POST.get('validate', False)
                parser = etree.XMLParser(ns_clean=True, remove_comments=True,
                                         remove_blank_text=True, encoding='utf-8')
                entity = etree.fromstring(metadata, parser)
                sp, errors = metadata_parser(entity, overwrite=False, verbosity=2,
                                             validate=validate, disable_checks=disable_checks)
                if sp:
                    sp.admins.add(request.user)
                    form = None
                    logger.info("Metadata for SP %s imported by %s"
                                .format(sp=sp, user=request.user))
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


def write_saml_metadata():
        # Generate metadata and write it to file
        metadata = metadata_generator_list(validated=True, privacypolicy=True, production=True)
        metadata_file = join(settings.METADATA_GIT_REPOSITORIO, settings.METADATA_FILENAME)
        with open(metadata_file, 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            # Hack for correcting namespace definition by removing prefix.
            f.write(etree.tostring(metadata, pretty_print=True,
                                   encoding='UTF-8').replace(b'xmlns:xmlns', b'xmlns'))


def write_ldap_metadata():
        # Generate metadata and write it to file
        tree = ldap_metadata_generator_list(validated=True, production=True)
        files = []
        metadata_file = join(settings.LDAP_GIT_REPOSITORIO, settings.LDAP_METADATA_FILENAME)
        files.append(settings.LDAP_METADATA_FILENAME)
        with open(metadata_file, 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            f.write(etree.tostring(tree, pretty_print=True, encoding='UTF-8'))
        # Generate separate files for all entities
        for entity in tree:
            entity_id = entity.get("ID")
            if entity_id:
                metadata_file = join(settings.LDAP_GIT_REPOSITORIO, entity_id + '.xml')
                files.append(entity_id + '.xml')
                with open(metadata_file, 'wb') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
                    f.write(etree.tostring(entity, pretty_print=True, encoding='UTF-8'))
        # Remove all other xml-files from repository
        for f in glob(settings.LDAP_GIT_REPOSITORIO + '*.xml'):
            if f.replace(settings.LDAP_GIT_REPOSITORIO, '') not in files:
                os.remove(f)
        return


@login_required
def metadata_management(request, service_type="saml"):
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
    if service_type == "saml" and hasattr(settings, 'METADATA_GIT_REPOSITORIO') and \
            hasattr(settings, 'METADATA_FILENAME'):
        repo_location = settings.METADATA_GIT_REPOSITORIO
    elif service_type == "ldap" and hasattr(settings, 'LDAP_GIT_REPOSITORIO') and \
            hasattr(settings, 'LDAP_METADATA_FILENAME'):
        repo_location = settings.LDAP_GIT_REPOSITORIO
    else:
        raise PermissionDenied
    try:
        repo = Repo(repo_location)
    except InvalidGitRepositoryError:
        error_message = _("Git repository appears to have an invalid format.")
        return render(request, "error.html", {'error_message': error_message})
    except NoSuchPathError:
        error_message = _("Repository path could not be accessed.")
        return render(request, "error.html", {'error_message': error_message})
    except GitCommandError:
        error_message = _("Execution of git command failed. Might want to try git command locally "
                          "from the command line and check that it works.")
        return render(request, "error.html", {'error_message': error_message})
    try:
        origin = repo.remotes.origin
    except AttributeError:
        error_message = _("Git repository has no origin.")
        return render(request, "error.html", {'error_message': error_message})
    diff = repo.git.diff('HEAD')
    log = last_commits(repo, 5)
    try:
        if repo.commit().hexsha != origin.fetch()[0].commit.hexsha:
            error = _("Remote repository not matching local, please fix manually.")
            return render(request, "rr/metadata_management.html", {'log': log,
                                                                   'error': error})
    except GitCommandError:
        error_message = _("Execution of git command failed. Might want to try git command locally "
                          "from the command line and check that it works.")
        return render(request, "error.html", {'error_message': error_message})
    if request.method == "POST":
        form = MetadataCommitForm(request.POST)
        if form.is_valid() and diff:
            commit_message = form.cleaned_data['commit_message']
            form_hash = form.cleaned_data['diff_hash']
            # Check that file has not changed
            if form_hash == hashlib.md5(diff.encode('utf-8')).hexdigest():
                repo.index.commit(commit_message)
                try:
                    origin.push()
                    log = last_commits(repo, 5)
                    if repo.commit().hexsha != origin.fetch()[0].commit.hexsha:
                        error = _("Pushing to remote did not work, please fix manually.")
                except GitCommandError:
                    error_message = _("Execution of git command failed. Might want to try git "
                                      "command locally  from the command line and check that it "
                                      "works.")
                return render(request, "rr/metadata_management.html", {'log': log,
                                                                       'error': error})
            else:
                error = _("Metadata file has changed, please try again.")
    if not error:
        if service_type == "saml":
            write_saml_metadata()
            repo.index.add([settings.METADATA_FILENAME])
        if service_type == "ldap":
            write_ldap_metadata()
            repo.git.add(A=True)
        diff = repo.git.diff('HEAD')
    diff_hash = hashlib.md5(diff.encode('utf-8')).hexdigest()
    form = MetadataCommitForm(diff_hash=diff_hash)
    return render(request, "rr/metadata_management.html", {'form': form,
                                                           'diff': diff,
                                                           'log': log,
                                                           'error': error})
