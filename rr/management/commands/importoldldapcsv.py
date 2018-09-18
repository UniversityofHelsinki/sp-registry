"""
Command line script for importing old CSV file for LDAP services

Usage help: ./manage.py importoldldapcsv -h
"""
from django.core.management.base import BaseCommand

from rr.utils.ldap_oldcsv_parser import ldap_oldcsv_parser

import csv


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', type=str, action='store',
                            dest='file', help='LDAP CSV file')
        parser.add_argument('-o', action='store_true', dest='overwrite',
                            help='Overwrite/add to existing LDAP SPs with same service name')
        parser.add_argument('-a', action='store_true', dest='validate',
                            help='Validate imported data automatically')

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        verbosity = int(options['verbosity'])
        validate = options['validate']
        file = options['file']
        if file:
            with open(file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    sp, errors = ldap_oldcsv_parser(row, overwrite, verbosity, validate)
                    for error in errors:
                        print(error)
