"""
Command line script for exporting ldap metadata

Usage help: ./manage.py exportldap -h
"""

from argparse import FileType
from lxml import etree
from sys import stdout

from django.core.management.base import BaseCommand

from rr.utils.ldap_metadata_generator import ldap_metadata_generator_list


class Command(BaseCommand):
    help = 'Exports LDAP metadata'

    def add_arguments(self, parser):
        parser.add_argument('-p', action='store_true', dest='production', help='Include production service providers')
        parser.add_argument('-m', type=FileType('w'), dest='metadata',
                            help='Metadata output file name')
        parser.add_argument('-i', type=str,  nargs='+', action='store', dest='include',
                            help='List of included entityIDs')
        parser.add_argument('-u', action='store_true', dest='unvalidated', help='Use unvalidated data')

    def handle(self, *args, **options):
        production = options['production']
        metadata_output = options['metadata'] if options['metadata'] else self.stdout
        include = options['include']
        validated = not options['unvalidated']
        if not production and not include:
            self.stderr.write("Give production tag or included entityIDs as command line arguments")
        if metadata_output:
            metadata = ldap_metadata_generator_list(validated, production, include)
            metadata_output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            metadata_output.write(etree.tostring(metadata, pretty_print=True, encoding='unicode'))
