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

ad={"peopletimestampreaders": ["createTimestamp","modifyTimestamp"],
"unitreaders": ["hyAccountingCode","hyDepartmentCode","hyDivisionCode","hyFacultyCode","hyUnitCode","hyProfitUnit","hyPersonEmployerCode","hyPersonSchoolCode","eduPersonPrimaryOrgUnitDN"],
"memberofreaders": ["memberOf"],
"employeenumberreaders": ["employeeNumber"],
"studentidreaders": ["funetEduPersonStudentID","schacPersonalUniqueCode"],
"languagereaders": ["preferredLanguage"],
"rolereaders": ["eduPersonAffiliation","eduPersonEntitlement","eduPersonPrimaryAffiliation","eduPersonPrincipalName","employeeNumber","schacHomeOrganization","schacHomeOrganizationType","hyPersonOodiSurrogateNumber"],
"hetureaders": ["funetEduPersonIdentityCode","schacPersonalUniqueID","schacDateOfBirth"],
"mailreaders": ["mail","hyPersonMailNode","mailLocalAddress","mailRoutingAddress"]}

csvtoaclgroup={'Yksikkötiedot':'unitreaders',
    'Ryhmäjäsenyydet':'memberofreaders',
    'Sähköpostiosoite':'mailreaders',
    'Haka-roolitieto':'rolereaders',
    'Henkilötunnus':'hetureaders',
    'Opiskelijanumero':'studentidreaders',
    'Henkilökuntanumero':'employeenumberreaders'}


def try_to_make_sure_attribute_exists(friendlyname):
    attribute = Attribute.objects.filter(friendlyname=friendlyname).first()
    if not attribute:
        name = ''
        attributeid = ''
        if friendlyname[0:2]=='hy':
            name = 'urn:mace:funet.fi:helsinki.fi:' + friendlyname
            attributeid = name
        if friendlyname=='funetEduPersonStudentID':
            attributeid = 'id-urn:mace:funet.fi:attribute-def:funetEduPersonStudentID'
            name = 'urn:oid:1.3.6.1.4.1.16161.1.1.10'
        Attribute.objects.create(name=name,
                                 public_saml=0,
                                 attributeid=attributeid,
                                 friendlyname=friendlyname,
                                 public_ldap=1)
    else:
        attribute.public_ldap=1
        attribute.save()


def parse_ldap_attributes(sp, d, validate, errors):
    """
    Parses LDAP client definition required attributes

    sp: ServiceProvider object where information is saved or linked
    d: dict containing ldap client definition
    validate: automatically validate added metadata
    errors: list of errors
    """

    specialanames=list(filter(lambda x: len(x)>0,map(lambda x: x.strip(),(d['Tarvittavat erikoisattribuutit']).split(' '))))
    groupedanames=[]

    for k in d.keys():
        if k in csvtoaclgroup.keys():
            groupedanames+=ad[csvtoaclgroup[k]]

    anames=specialanames + groupedanames

    for friendlyname in anames:
        try_to_make_sure_attribute_exists(friendlyname)
        attribute = Attribute.objects.filter(friendlyname=friendlyname).first()
        if attribute:
            if not SPAttribute.objects.filter(sp=sp, attribute=attribute).exists():
                validated = None
                if validate:
                    validated=timezone.now()
                SPAttribute.objects.create(sp=sp,
                                           attribute=attribute,
                                           reason="initial import, please give the real reason or remove attribute if not needed",
                                           validated=validated)
        else:
            errors.append(sp.name_fi + " : " + _("Could not add attribute") + " : " + friendlyname)

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
    
def make_usergroup(sp, name, validate):
    if not name:
        name = " "
    if not UserGroup.objects.filter(sp=sp, name=name).exists():
        if validate:
            UserGroup.objects.create(sp=sp,
                                   name=name,
                                   validated=timezone.now())
        else:
            UserGroup.objects.create(sp=sp,
                                   name=name,
                                   validated=None)


def parse_ldap_groups(sp, d, validate, errors):
    """
    Parses LDAP user groups for the client

    sp: ServiceProvider object where information is linked
    d: LDAP client description dict which is parsed
    validate: automatically validate added metadata
    """
#    ug_s=d['Tarvittavat ryhmät']
#    if ug_s=='Kaikki':
#        errors.append("LDAP Group parser: %s: support to add access for all groups not implemented yet in the registry" % sp.name_fi)
#        return

    usergroups=list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), ug_s.split(' '))))
    for u in usergroups:
        make_usergroup(sp, u, validate)


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

    parse_ldap_attributes(sp, d, validate, errors)

    parse_ldap_groups(sp, d, validate, errors)


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
