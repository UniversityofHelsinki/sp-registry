"""
Remove LDAP server name from providers.

Usage help: ./manage.py removeservername -h
"""

import logging

from django.core.management.base import BaseCommand

from rr.models.serviceprovider import ServiceProvider
from rr.utils.serviceprovider import create_sp_history_copy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    list_only = False

    def add_arguments(self, parser):
        parser.add_argument("-l", action="store_true", dest="list_only", help="List only, do not remove")
        parser.add_argument(
            "--host", action="append", default=[], dest="hosts", help="Hostname, you can use multiple --host options"
        )

    def output(self, text):
        if self.list_only:
            self.stdout.write("(List only) " + text)
        else:
            logger.info(text)

    def find_services(self, hostname):
        return ServiceProvider.objects.filter(end_at=None, server_names__icontains=hostname)

    def remove_server_name(self, service, hostname):
        self.output(f"Removing server name: {hostname} from service provider {service.entity_id}")
        if not self.list_only:
            sp = ServiceProvider.objects.get(pk=service.pk)
            if sp.validated:
                create_sp_history_copy(sp)
            service.validated = None
            service.server_names = "\n".join(service.server_names.replace(hostname, "").split())
            service.save_modified()

    def handle(self, *args, **options):
        hosts = options["hosts"]
        self.list_only = options["list_only"] | False
        for hostname in hosts:
            services = self.find_services(hostname)
            if not services:
                self.output(f"No services found with server name: {hostname}")
            for service in services:
                self.remove_server_name(service, hostname)
