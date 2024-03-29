"""
Command line script for decrypting client_secrets in JSON metadata file.

Usage help: ./manage.py decryptclientsecret -h
"""

import json
from argparse import FileType
from sys import stdin, stdout

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            type=FileType("r"),
            dest="input",
            nargs="?",
            default=stdin,
            help="Input JSON file, defaults to stdin.",
        )
        parser.add_argument("-o", type=FileType("w"), dest="output", help="Output JSON file, defaults to stdout.")

    @staticmethod
    def get_client_secret(encrypted_client_secret):
        """Returns decrypted client secret in text."""
        if encrypted_client_secret and hasattr(settings, "OIDC_CLIENT_SECRET_KEY") and settings.OIDC_CLIENT_SECRET_KEY:
            key = settings.OIDC_CLIENT_SECRET_KEY.encode()
            try:
                f = Fernet(key)
                return f.decrypt(encrypted_client_secret.encode()).decode()
            except TypeError:
                return None
            except InvalidToken:
                print("ERROR, secret is not a valid Fernet token: %s " % encrypted_client_secret)
                return None
        return None

    def handle(self, *args, **options):
        input_file = options["input"]
        output_file = options["output"] if options["output"] else self.stdout
        error = False
        if input_file and output_file:
            data = json.load(input_file)
            for service in data:
                if "client_secret" in service:
                    encrypted_secret = service["client_secret"]
                    decrypted_secret = self.get_client_secret(encrypted_secret)
                    if decrypted_secret:
                        service["client_secret"] = decrypted_secret
                    else:
                        error = True
            if not error:
                output_file.write(json.dumps(data, indent=4, sort_keys=True))
