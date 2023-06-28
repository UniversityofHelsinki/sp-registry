"""
Command line script for exporting metadata

Usage help: ./manage.py exportmetadata -h
"""

import hashlib
import os
from argparse import FileType

from django.conf import settings
from django.core.management.base import BaseCommand
from lxml import etree

from rr.models.serviceprovider import ServiceProvider
from rr.utils.saml_metadata_generator import (
    saml_metadata_generator,
    saml_metadata_generator_list,
)


class Command(BaseCommand):
    help = "Exports validated metadata"

    def add_arguments(self, parser):
        parser.add_argument("-p", action="store_true", dest="production", help="Include production service providers")
        parser.add_argument("-t", action="store_true", dest="test", help="Include test service providers")
        parser.add_argument("-m", type=FileType("w"), dest="metadata", help="Metadata output file name")
        parser.add_argument("-d", type=str, dest="metadata_dir", help="Metadata directory for individual files")
        parser.add_argument(
            "-i", type=str, nargs="+", action="store", dest="include", help="List of included entityIDs"
        )
        parser.add_argument("-u", action="store_true", dest="unvalidated", help="Use unvalidated data")
        parser.add_argument(
            "-x", action="store_true", dest="privacypolicy", help="Replace missing privacypolicy for HY"
        )

    def handle(self, *args, **options):
        production = options["production"]
        test = options["test"]
        metadata_output = options["metadata"] if options["metadata"] else self.stdout
        metadata_dir = options["metadata_dir"]
        include = options["include"]
        validated = not options["unvalidated"]
        privacypolicy = options["privacypolicy"]
        if not production and not test and not include:
            self.stderr.write(
                "Give production, test or included entityIDs as command line " 'arguments, use "-h" for help.'
            )
            exit(1)
        # Create XML containing selected EntityDescriptors
        if not metadata_dir:
            metadata = saml_metadata_generator_list(validated, privacypolicy, production, test, include)
            metadata_output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            # Hack for correcting namespace definition by removing prefix.
            metadata_output.write(
                etree.tostring(metadata, pretty_print=True, encoding=str).replace("xmlns:xmlns", "xmlns")
            )
        else:
            metadata_list = saml_metadata_generator_list(
                validated, privacypolicy, production, test, include, as_list=True
            )
            for metadata in metadata_list:
                if metadata is not None and metadata.get("entityID"):
                    file_name = hashlib.sha1(metadata.get("entityID").encode()).hexdigest() + ".xml"
                    try:
                        with open(os.path.join(metadata_dir, file_name), "w") as f:
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                            f.write(
                                etree.tostring(metadata, pretty_print=True, encoding=str).replace(
                                    "xmlns:xmlns", "xmlns"
                                )
                            )
                    except FileNotFoundError:
                        self.stderr.write("Directory does not exist.")
                        exit(1)
