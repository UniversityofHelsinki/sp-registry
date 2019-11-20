"""
Functions for generating metadata of OIDC relying parties
"""

import json
import logging

from django.db.models import Q

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.redirecturi import RedirectUri
from rr.utils.metadata_generator_common import get_entity

logger = logging.getLogger(__name__)


def metadata_uiinfo(metadata, sp, privacypolicy):
    """
    Generates uiinfo for RP metadata

    metadata: RP metadata object
    sp: ServiceProvider object
    privacypolicy: fill empty privacypolicy URLs with default value

    return RP metadata objet
    """

    if sp.name_fi:
        metadata['client_name#fi'] = sp.name_fi
    if sp.name_en:
        metadata['client_name#en'] = sp.name_en
    if sp.name_sv:
        metadata['client_name#sv'] = sp.name_sv

    if sp.privacypolicy_fi:
        metadata['policy_uri#fi'] = sp.privacypolicy_fi
    elif sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
        metadata['policy_uri#fi'] = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet"
    if sp.privacypolicy_en:
        metadata['policy_uri#en'] = sp.privacypolicy_en
    elif sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
        metadata['policy_uri#en'] = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet"
    if sp.privacypolicy_sv:
        metadata['policy_uri#sv'] = sp.privacypolicy_sv
    elif sp.organization and sp.organization.name_fi == "Helsingin yliopisto" and privacypolicy:
        metadata['policy_uri#sv'] = "https://www.helsinki.fi/fi/yliopisto/tietosuojaselosteet"
    return metadata


def metadata_claims(sp, validation_date):
    """
    Generates claims for RP metadata

    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """
    if validation_date:
        attributes = SPAttribute.objects.filter(sp=sp).filter(
            Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
    claims = {}
    attributes_id_token = attributes.filter(oidc_id_token=True)
    if attributes_id_token:
        claims['id_token'] = {}
        for attribute in attributes_id_token:
            claims['id_token'][attribute.attribute.oidc_claim] = None
    attributes_userinfo = attributes.filter(oidc_userinfo=True)
    if attributes_userinfo:
        claims['userinfo'] = {}
        for attribute in attributes_userinfo:
            claims['userinfo'][attribute.attribute.oidc_claim] = None
    return claims


def metadata_redirect_uris(sp, validation_date):
    """
    Generates redirect_uris for RP metadata

    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata

    Using CamelCase instead of regular underscore attribute names in element tree.
    """

    if validation_date:
        redirect_uris = RedirectUri.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        redirect_uris = RedirectUri.objects.filter(sp=sp, end_at=None)
    return list(redirect_uris.values_list('uri', flat=True))


def oidc_metadata_generator(sp, validated=True, privacypolicy=False, client_secret_encryption=None):
    """
    Generates metadata for single RP.

    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    privacypolicy: fill empty privacypolicy URLs with default value
    client_secret_encryption: set to "encrypted" for encrypted client secrets,
      "decrypted" for decrypted. Otherwise the client secret is obfuscated.

    return json object
    """
    metadata = {}
    entity, history, validation_date = get_entity(sp, validated)
    if not entity:
        return metadata
    metadata['client_id'] = entity.entity_id
    metadata = _set_client_secret(entity, metadata, client_secret_encryption)
    if entity.jwks_uri:
        metadata['jwks_uri'] = entity.jwks_uri
    elif entity.jwks:
        metadata['jwks'] = json.loads(entity.jwks)
    metadata['application_type'] = entity.application_type
    if entity.subject_identifier:
        metadata['subject_type'] = entity.subject_identifier
    grant_types = entity.grant_types.all()
    response_types = entity.response_types.all()
    oidc_scopes = entity.oidc_scopes.all()
    redirect_uris = metadata_redirect_uris(sp=sp, validation_date=validation_date)
    claims = metadata_claims(sp=sp, validation_date=validation_date)
    if redirect_uris:
        metadata['redirect_uris'] = redirect_uris
    if claims:
        metadata['claims'] = claims
    if grant_types:
        metadata['grant_types'] = list(grant_types.values_list('name', flat=True))
    if response_types:
        metadata['response_types'] = list(response_types.values_list('name', flat=True))
    else:
        metadata['response_types'] = ["none"]
    scopes = ['openid']
    if oidc_scopes:
        scopes = scopes + list(oidc_scopes.values_list('name', flat=True))
    metadata['scope'] = ' '.join(map(str, scopes))
    metadata = metadata_uiinfo(metadata, entity, privacypolicy)
    return metadata


def _set_client_secret(entity, metadata, client_secret_encryption):
    if entity.encrypted_client_secret and entity.application_type != 'native' and not (entity.jwks or entity.jwks_uri):
        if client_secret_encryption == "encrypted":
            metadata['client_secret'] = entity.encrypted_client_secret
        elif client_secret_encryption == "decrypted":
            try:
                metadata['client_secret'] = entity.get_client_secret().decode()
            except AttributeError:
                return None
        else:
            metadata['client_secret'] = "******"
    return metadata


def oidc_metadata_generator_list(validated=True, privacypolicy=False, production=False, test=False, include=None,
                                 client_secret_encryption=None):
    """
    Generates metadata for list of OIDC RPs.

    validated: if false, using unvalidated metadata
    privacypolicy: replace privacy policy if missing
    production: include production SPs
    test: include test SPs
    include: include listed SPs
    client_secret_encryption: set to "encrypted" for encrypted client secrets,
      "decrypted" for decrypted. Otherwise the client secret is obfuscated.

    return json object list
    """
    metadata = []
    serviceproviders = ServiceProvider.objects.filter(end_at=None, service_type="oidc")
    for sp in serviceproviders:
        if (production and sp.production) or (test and sp.test) or (include and sp.entity_id in include):
            sp_metadata = oidc_metadata_generator(sp, validated, privacypolicy, client_secret_encryption)
            if sp_metadata:
                metadata.append(sp_metadata)
            else:
                return None
    return metadata
