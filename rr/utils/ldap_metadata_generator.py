"""
Functions for genereating metadata of service providers
"""
import logging

from lxml import etree
from django.db.models import Q

from rr.models.serviceprovider import SPAttribute, ServiceProvider
from rr.models.usergroup import UserGroup
from rr.utils.metadata_generator_common import get_entity

logger = logging.getLogger(__name__)


def ldap_metadata_usergroups(element, sp, validation_date):
    """
    Generates userGroups elements for SP metadata XML

    element: etree.Element object for previous level (SPSSODescriptor)
    sp: ServiceProvider object
    validation_date: if None, using unvalidated metadata
    """
    if validation_date:
        usergroups = UserGroup.objects.filter(sp=sp).filter(Q(end_at=None) |
                                                            Q(end_at__gt=validation_date)).exclude(validated=None)
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
        attributes = SPAttribute.objects.filter(sp=sp).filter(Q(end_at=None) |
                                                              Q(end_at__gt=validation_date)).exclude(validated=None)
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
    provider, history, validation_date = get_entity(sp, validated)
    if not provider:
        return tree
    if validation_date:
        entity = etree.SubElement(tree, "Entity", ID=provider.entity_id,
                                  validated=validation_date.strftime('%Y-%m-%dT%H:%M:%S%z'))
    else:
        entity = etree.SubElement(tree, "Entity", ID=provider.entity_id, validated="false")
    if provider.server_names:
        servers_element = etree.SubElement(entity, "Servers")
        servers = provider.server_names.splitlines()
        for server in servers:
            etree.SubElement(servers_element, "Server", name=server)
    etree.SubElement(entity, "TargetGroup", value=provider.target_group)
    if provider.contacts:
        contacts_element = etree.SubElement(entity, "Contacts")
        contacts = Contact.objects.filter(sp=provider, end_at=None)
        for contact in contacts:
            etree.SubElement(contacts_element, "Contact", email=contact.email, contacttype=contact.type)
    if provider.service_account:
        etree.SubElement(entity, "ServiceAccount", contact=provider.service_account_contact, value="true")
    else:
        etree.SubElement(entity, "ServiceAccount", value="false")
    if provider.local_storage_users:
        etree.SubElement(entity, "LocalStorageUsers", value="true")
    else:
        etree.SubElement(entity, "LocalStorageUsers", value="false")
    if provider.local_storage_groups:
        etree.SubElement(entity, "LocalStorageGroups", value="true")
    else:
        etree.SubElement(entity, "LocalStorageGroups", value="false")
    if provider.can_access_all_ldap_groups:
        etree.SubElement(entity, "CanAccessAllLdapGroups", value="true")
    else:
        etree.SubElement(entity, "CanAccessAllLdapGroups", value="false")
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
    for sp in filter(lambda x: not x.uses_ldapauth, serviceproviders):
        if (production and sp.production) or (include and sp.entity_id in include):
            ldap_metadata_generator(sp, validated, tree)
    return tree
