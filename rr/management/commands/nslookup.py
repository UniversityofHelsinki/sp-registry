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

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', action='store_true', dest='check_saml',
                            help='Check SAML services')
        parser.add_argument('-l', action='store_true', dest='check_ldap',
                            help='Check LDAP services')
        parser.add_argument('-a', action='store_true', dest='test_all',
                            help='Test all services. This tests only production by default')

    def handle(self, *args, **options):
        check_saml = options['check_saml']
        check_ldap = options['check_ldap']
        test_all = options['test_all']
        if test_all:
            services = ServiceProvider.objects.filter(end_at=None,
                                                      history=None).order_by('service_type',
                                                                             'entity_id')
        else:
            services = ServiceProvider.objects.filter(end_at=None, history=None,
                                                      production=True).order_by('service_type',
                                                                                'entity_id')
        if check_saml and not check_ldap:
            services = services.filter(service_type="saml")
        elif check_ldap and not check_saml:
            services = services.filter(service_type="ldap")
        for sp in services:
            if sp.service_type == "saml":
                endpoints = []
                for endpoint in Endpoint.objects.filter(sp=sp, end_at=None).values_list('url',
                                                                                        flat=True):
                    endpoints.append(urlparse(endpoint).netloc.split(":")[0])
                for endpoint in set(endpoints):
                    try:
                        getaddrinfo(endpoint, None)
                    except gaierror:
                        print("Address does not resolve | SAML entity: %s | address: %s" %
                              (sp.entity_id, endpoint))
            if sp.service_type == "ldap":
                for server_address in sp.server_names.splitlines():
                    try:
                        getaddrinfo(server_address.strip(), None)
                    except gaierror:
                        print("Address does not resolve | LDAP entity: %s | address: %s" %
                              (sp.entity_id, server_address))
