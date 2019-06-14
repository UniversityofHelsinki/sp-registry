"""
Command line script for exporting OIDC metadata

Usage help: ./manage.py cleandb -h
"""

import json

from django.core.management.base import BaseCommand

from rr.utils.oidc_metadata_generator import oidc_metadata_generator_list


class Command(BaseCommand):
    help = 'Exports validated metadata'

    def add_arguments(self, parser):
        parser.add_argument('-p', action='store_true', dest='production',
                            help='Include production service providers')
        parser.add_argument('-t', action='store_true', dest='test',
                            help='Include test service providers')
        parser.add_argument('-m', type=str, action='store', dest='metadata',
                            help='Metadata output file name')
        parser.add_argument('-e', action='store_true', dest='encryption',
                            help='Encrypt client secrets')
        parser.add_argument('-i', type=str,  nargs='+', action='store', dest='include',
                            help='List of included client IDs')
        parser.add_argument('-u', action='store_true', dest='unvalidated',
                            help='Use unvalidated data')
        parser.add_argument('-x', action='store_true', dest='privacypolicy',
                            help='Replace missing privacypolicy for HY')

    def handle(self, *args, **options):
        production = options['production']
        test = options['test']
        metadata_output = options['metadata']
        if options['encryption']:
            encryption = "encrypted"
        else:
            encryption = "decrypted"
        include = options['include']
        validated = not options['unvalidated']
        privacypolicy = options['privacypolicy']
        if not production and not test and not include:
            self.stdout.write("Give production, test or included client IDs as command line "
                              "arguments")
        # Create XML containing selected EntityDescriptors
        if metadata_output:
            metadata = oidc_metadata_generator_list(validated=validated,
                                                    privacypolicy=privacypolicy,
                                                    production=production,
                                                    test=test,
                                                    include=include,
                                                    client_secret_encryption=encryption)
            if metadata is None:
                self.stdout.write("Could not create metadata, check log for more information.")
            else:
                with open(metadata_output, 'w') as f:
                    f.write(json.dumps(metadata, indent=4, sort_keys=True))
