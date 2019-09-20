"""
Check that addresses are found in DNS

Usage help: ./manage.py nslookup
"""
import logging

from urllib.parse import urlparse
from _socket import getaddrinfo, gaierror

from django.core.management.base import BaseCommand

from rr.models.serviceprovider import ServiceProvider
from rr.models.endpoint import Endpoint
from rr.models.redirecturi import RedirectUri

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', action='store_true', dest='check_saml',
                            help='Check SAML services')
        parser.add_argument('-l', action='store_true', dest='check_ldap',
                            help='Check LDAP services')
        parser.add_argument('-o', action='store_true', dest='check_oidc',
                            help='Check OIDC services')
        parser.add_argument('-a', action='store_true', dest='test_all',
                            help='Test all services. Script tests only production by default')

    def handle(self, *args, **options):
        check_saml = options['check_saml']
        check_ldap = options['check_ldap']
        check_oidc = options['check_oidc']
        test_all = options['test_all']
        if test_all:
            services = ServiceProvider.objects.filter(end_at=None,
                                                      history=None).order_by('service_type',
                                                                             'entity_id')
        else:
            services = ServiceProvider.objects.filter(end_at=None, history=None,
                                                      production=True).order_by('service_type',
                                                                                'entity_id')
        if not check_saml:
            services = services.exclude(service_type="saml")
        if not check_ldap:
            services = services.exclude(service_type="ldap")
        if not check_oidc:
            services = services.exclude(service_type="oidc")
        for sp in services:
            if sp.service_type == "saml":
                self._check_saml_service(sp)
            if sp.service_type == "ldap":
                self._check_ldap_service(sp)
            if sp.service_type == "oidc":
                self._check_oidc_service(sp)

    @staticmethod
    def _check_saml_service(sp):
        endpoints = []
        for endpoint in Endpoint.objects.filter(sp=sp, end_at=None).values_list('location', flat=True):
            endpoints.append(urlparse(endpoint).netloc.split(":")[0])
        for endpoint in set(endpoints):
            try:
                getaddrinfo(endpoint, None)
            except gaierror:
                print("Address does not resolve | SAML entity: %s | address: %s" %
                      (sp.entity_id, endpoint))

    @staticmethod
    def _check_oidc_service(sp):
        redirecturis = []
        for redirecuri in RedirectUri.objects.filter(sp=sp, end_at=None).values_list('uri', flat=True):
            redirecturis.append(urlparse(redirecuri).netloc.split(":")[0])
        for redirecuri in set(redirecturis):
            try:
                getaddrinfo(redirecuri, None)
            except gaierror:
                print("Address does not resolve | OIDC entity: %s | address: %s" %
                      (sp.entity_id, redirecuri))

    @staticmethod
    def _check_ldap_service(sp):
        for server_address in sp.server_names.splitlines():
            try:
                getaddrinfo(server_address.strip(), None)
            except gaierror:
                print("Address does not resolve | LDAP entity: %s | address: %s" %
                      (sp.entity_id, server_address))
