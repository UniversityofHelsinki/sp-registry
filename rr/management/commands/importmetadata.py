"""
Command line script for importing metadata.xml

Usage help: ./manage.py cleandb -h
"""
from lxml import etree

from django.core.management.base import BaseCommand

from rr.utils.saml_metadata_parser import saml_metadata_parser


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', type=str,  nargs='+', action='store',
                            dest='files', help='List of files')
        parser.add_argument('-o', action='store_true', dest='overwrite',
                            help='Overwrite/add to existing SPs with same entity_id')
        parser.add_argument('-d', action='store_true', dest='disable',
                            help='Disable check for endpoint bindings')
        parser.add_argument('-a', action='store_true', dest='validate',
                            help='Validate imported metadata automatically')

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        verbosity = int(options['verbosity'])
        validate = options['validate']
        disable = options['disable']
        files = options['files']
        if files:
            for filename in files:
                parser = etree.XMLParser(
                    ns_clean=True, remove_comments=True, remove_blank_text=True, resolve_entities=False,
                    no_network=True)
                tree = etree.parse(filename, parser)
                if not tree:
                    print("File does not exist: " + filename)
                else:
                    root = tree.getroot()
                    for entity in root:
                        sp, errors = saml_metadata_parser(entity, overwrite, verbosity, validate,
                                                          disable)
                        for error in errors:
                            print(error)
