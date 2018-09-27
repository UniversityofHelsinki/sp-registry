"""
Functions for importing LDAP SP definitions from old style CSV file
"""

from rr.models.serviceprovider import ServiceProvider, SPAttribute
from rr.models.contact import Contact
from rr.models.attribute import Attribute
from rr.models.ldap import Ldap
from rr.models.usergroup import UserGroup
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
import logging
import csv

logger = logging.getLogger(__name__)

def parse_ldap_attributes(sp, d, validate, errors):
    """
    Parses LDAP client definition required attributes

    sp: ServiceProvider object where information is saved or linked
    d: dict containing ldap client definition
    validate: automatically validate added metadata
    errors: list of errors
    """
#    for child in element:
#        if etree.QName(child.tag).localname == "RequestedAttribute":
#            friendlyname = child.get("FriendlyName")
#            name = child.get("Name")
#            if friendlyname:
#                attribute = Attribute.objects.filter(name=name).first()
#                if not attribute:
#                    attribute = Attribute.objects.filter(friendlyname=friendlyname).first()
#                if attribute:
#                    if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
#                        if validate:
#                            SPAttribute.objects.create(sp=sp,
#                                                       attribute=attribute,
#                                                       reason="initial dump, please give the real reason",
#                                                       validated=timezone.now())
#                        else:
#                            SPAttribute.objects.create(sp=sp,
#                                                       attribute=attribute,
#                                                       reason="initial dump, please give the real reason",
#                                                       validated=None)
#                else:
#                    errors.append(sp.entity_id + " : " + _("Could not add attribute") + " : " + friendlyname + ", " + name)
#        if etree.QName(child.tag).localname == "ServiceName":
#            if child.values()[0] == "fi":
#                sp.name_fi = child.text
#            elif child.values()[0] == "en":
#                sp.name_en = child.text
#            elif child.values()[0] == "sv":
#                sp.name_sv = child.text
#        if etree.QName(child.tag).localname == "ServiceDescription":
#            if child.values()[0] == "fi":
#                sp.description_fi = child.text
#            elif child.values()[0] == "en":
#                sp.description_en = child.text
#            elif child.values()[0] == "sv":
#                sp.description_sv = child.text


def add_ldap_spadmin(sp, maileppn, validate, errors):
    (adminemail,eppn) = maileppn.split('=')

    admin = User.objects.filter(username=eppn).first()
    
    if not admin:
        admin = User(username=eppn,
                     password=User.objects.make_random_password(),
                     email=adminemail,
                     is_active=True)
        admin.set_unusable_password = True
        admin.save()

    sp.admins.add(admin)

def parse_ldap_spadmins(sp, d, validate, errors):
    for maileppn in filter(lambda x: len(x)>0, d['SP-adminit'].split(',')):
        add_ldap_spadmin(sp, maileppn, validate, errors)
    
def make_contact(sp, contacttype, namel, email, validate):
    firstname = ' '.join(namel[0:-1]).strip()
    lastname = namel[-1].strip()
    email = email.strip()
    
    if not firstname:
        firstname = " "
    if not lastname:
        lastname = " "
    if not Contact.objects.filter(sp=sp, type=contacttype, firstname=firstname, lastname=lastname, email=email).exists() and email:
        if validate:
            Contact.objects.create(sp=sp,
                                   type=contacttype,
                                   firstname=firstname,
                                   lastname=lastname,
                                   email=email,
                                   validated=timezone.now())
        else:
            Contact.objects.create(sp=sp,
                                   type=contacttype,
                                   firstname=firstname,
                                   lastname=lastname,
                                   email=email,
                                   validated=None)

def parse_ldap_contacts(sp, d, validate, errors):
    """
    Parses LDAP client contact information

    sp: ServiceProvider object where information is linked
    d: LDAP client description dict which is parsed
    validate: automatically validate added metadata
    """
    ownernamel=d['Omistajan nimi yliopistolla'].split(' ')
    email = d['Omistajan sähköpostiosoite yliopistolla']
    make_contact(sp, 'administrative', ownernamel, email, validate)

    adminnames=d['Ylläpitäjien nimet'].split(',')
    adminemails=d['Ylläpitäjien sähköpostiosoitteet'].split(',')

    diff = len(adminnames) - len(adminemails)
    if diff < 0:
        adminnames += ((-1) * diff) * ['']
    if diff > 0:
        adminemails += diff * adminemails[-1:]

    if len(adminnames) == len(adminemails): # normal case
        admins=zip(adminnames,adminemails)
        for admin in admins:
            adminnamel=admin[0].strip().split(' ')
            email = admin[1]
            make_contact(sp, 'technical', adminnamel, email, validate)
    else:
        errors.append("LDAP contact parser: %s: couldn't make admin email and name lists the same length, didn't add tech contacts" % sp.name_fi)

def parse_ldapdict(sp, d, validate, errors):
    """
    Parses LDAP SP dictionary

    sp: ServiceProvider object where information is saved or linked
    d: Python dictionary where LDAP client information is stored
    validate: automatically validate added metadata
    errors: list of errors
    """

    ppdata=d['Onko järjestelmällä rekisteriseloste: Onko rekisteriseloste olemassa'].split(',')
    if ppdata[0] == 'rekiseriselosteon':
            sp.privacypolicy_fi = "http://example.org/privacypolicy_exists"
    else:
            sp.privacypolicy_fi = "http://example.org/privacypolicy_does_not_exist"
    if len(ppdata)==2:
        sp.privacypolicy_fi = ppdata[1]
    sp.notes = d['Mahdolliset lisätiedot']
    if d['Käyttötapaus'] == 'groupsync':
            sp.local_storage_groups = True
    else:
            sp.local_storage_groups = False
    if d['Käyttötapaus'] == 'usersync':
            sp.local_storage_users = True
    else:
            sp.local_storage_users = False
    if d['Tallentaako järjestelmä käyttäjien antamat salasanat: Tallennetaanko käyttäjän salasana'] == 'salasanatallennetaan':
            sp.local_storage_passwords = True
    else:
            sp.local_storage_passwords = False
    sp.server_names='\n'.join(filter(lambda x: x!= '', d['Palvelimien täydelliset nimet välilyönnillä erotettuina (ei ip-osoitetta)'].split(' ')))
    if d['Onko järjestelmän tiedot yliopiston Sovellussalkussa: Tiedot on Sovellussalkussa'] == 'sovellussalkussaon':
            sp.application_portfolio = "http://example.org/portfolio_exists"
    else:
            sp.application_portfolio = "http://example.org/portfolio_does_not_exist"
    if d['Palvelutunnuksen käyttö: Osaako sovellus käyttää palvelutunnusta'] == 'Kyllä':
            sp.service_account = True
    else:
            sp.service_account = False
    sacl = [d['Henkilökohtainen @helsinki.fi muotoinen sähköpostiosoite'], d['Saman henkilön kännykkänumero']]
    if len(sacl) > 0:
        sp.service_account_contact = ' '.join(sacl)
    targetgroupmap = {'restricted': 'restricted',
        'hy': 'university',
        'public' : 'internet'}
    sp.target_group = targetgroupmap[d['Kohderyhmä: Palvelun käyttölaajuus']]

    parse_ldap_contacts(sp, d, validate, errors)

    parse_ldap_spadmins(sp, d, validate, errors)


def ldap_oldcsv_parser(entity, overwrite, verbosity, validate=False):
    """
    Parses LDAP CSV dict and saves information to SP-object

    entity: LDAP CSV dict for one SP
    overwrite: replace/add data for existing SP
    verbosity: verbosity level for errors
    validate: automatically validate added metadata

    return sp and possible errors
    """
    errors = []
    name = entity['Palvelun tai järjestelmän nimi']
    skip = False
    if name:
        try:
            sp = ServiceProvider.objects.get(name_fi=name, end_at=None)
            if not overwrite:
                skip = True
                if verbosity > 1:
                    errors.append(name + " : " + _("Name already exists, skipping"))
            else:
                if verbosity > 1:
                    errors.append(name + " : " + _("Name already exists, overwriting"))
        except ServiceProvider.DoesNotExist:
            n = 1
            while True:
                entityID = "ldap-" + str(n)
                if not ServiceProvider.objects.filter(entity_id=entityID).exists():
                    break
                n = n + 1
            if validate:
                sp = ServiceProvider.objects.create(entity_id=entityID, name_fi=name, service_type="ldap", validated=timezone.now(), modified=False)
            else:
                sp = ServiceProvider.objects.create(entity_id=entityID, name_fi=name, service_type="ldap", validated=None, modified=True)
            if verbosity > 2:
                errors.append(name + " : " + _("Name does not exist, creating"))
        if not skip:
            parse_ldapdict(sp, entity, validate, errors)
            sp.save()
            return sp, errors
    else:
        errors.append(_("Could not find name"))
    return None, errors
