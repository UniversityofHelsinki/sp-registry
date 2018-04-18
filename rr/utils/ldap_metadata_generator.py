"""
Functions for genereating metadata of service providers
"""

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.usergroup import UserGroup
from lxml import etree
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


def ldap_metadata_usergroups(element, sp, validation_date):
    """
    Generates userGroups elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """
    if validation_date:
        usergroups = UserGroup.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        usergroups = UserGroup.objects.filter(sp=sp, end_at=None)
    entity = etree.SubElement(element, "UserGroups")
    for usergroup in usergroups:
        etree.SubElement(entity, "UserGroup",
                         name=usergroup.name)


def ldap_metadata_attributes(element, sp, validation_date):
    """
    Generates userGroups elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """
    if validation_date:
        attributes = SPAttribute.objects.filter(sp=sp).filter(Q(end_at=None) | Q(end_at__gt=validation_date)).exclude(validated=None)
    else:
        attributes = SPAttribute.objects.filter(sp=sp, end_at=None)
    attribute_groups = attributes.order_by().values_list('attribute__group').distinct()
    entity = etree.SubElement(element, "AttributeGroups")
    for group in attribute_groups:
        if group[0]:
            etree.SubElement(entity, "AttributeGroup", name=group[0])
    attributes_without_group = attributes.filter(attribute__group="")
    entity = etree.SubElement(element, "Attributes")
    for attribute in attributes_without_group:
        etree.SubElement(entity, "Attribute", friendlyName=attribute.attribute.friendlyname)


def ldap_metadata_generator(sp, validated=True, tree=None):
    """
    Generates metadata for single SP.

    sp: ServiceProvider object
    validated: if false, using unvalidated metadata
    tree: use as root if given, generate new root if not

    return tree
    """

    if validated and not sp.validated:
        history = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
        if not history:
            return tree
        validation_date = history.validated
    else:
        history = None
        if validated:
            validation_date = sp.validated
        else:
            validation_date = None
    if history:
        entity_id = history.entity_id
    else:
        entity_id = sp.entity_id
    if validation_date:
        entity = etree.SubElement(tree, "Entity", ID=entity_id, validated=validation_date.strftime('%Y%m%d %H:%M:%S'))
    else:
        entity = etree.SubElement(tree, "Entity", ID=entity_id, validated="false")
    if history:
        etree.SubElement(entity, "ServerNames", value=history.server_names)
        etree.SubElement(entity, "TargetGroup", value=history.target_group)
        if history.service_account:
            etree.SubElement(entity, "ServiceAccount", value="true", contact=history.service_account_contact)
        else:
            etree.SubElement(entity, "ServiceAccount", value="false")
        if history.local_storage_users:
            etree.SubElement(entity, "LocalStorageUsers", value="true")
        else:
            etree.SubElement(entity, "LocalStorageUsers", value="false")
        if history.local_storage_groups:
            etree.SubElement(entity, "LocalStorageGroups", value="true")
        else:
            etree.SubElement(entity, "LocalStorageGroups", value="false")
    else:
        etree.SubElement(entity, "ServerNames", value=sp.server_names)
        etree.SubElement(entity, "TargetGroup", value=sp.target_group)
        if sp.service_account:
            etree.SubElement(entity, "ServiceAccount", value="true", contact=sp.service_account_contact)
        else:
            etree.SubElement(entity, "ServiceAccount", value="false")
        if sp.local_storage_users:
            etree.SubElement(entity, "LocalStorageUsers", value="true")
        else:
            etree.SubElement(entity, "LocalStorageUsers", value="false")
        if sp.local_storage_groups:
            etree.SubElement(entity, "LocalStorageGroups", value="true")
        else:
            etree.SubElement(entity, "LocalStorageGroups", value="false")
    ldap_metadata_attributes(entity, sp, validation_date)
    ldap_metadata_usergroups(entity, sp, validation_date)
    return tree


def ldap_metadata_generator_list(validated=True, production=False, include=None):
    """
    Generates metadata for list of serviceproviders.

    validated: if false, using unvalidated metadata
    production: include production SPs
    include: include listed SPs

    return tree

    Using CamelCase instead of regular underscore attribute names in element tree.
    """
    tree = etree.Element("LdapEntities", Name="ldap2015.helsinki.fi")
    serviceproviders = ServiceProvider.objects.filter(end_at=None, service_type="ldap")
    for sp in serviceproviders:
        if production and sp.production:
            ldap_metadata_generator(sp, validated, tree)
        elif include and sp.entity_id in include:
            ldap_metadata_generator(sp, validated, tree)
    return tree
