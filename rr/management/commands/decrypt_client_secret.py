"""
Command line script for descrypting client_secrets in JSON metadata file.

Usage help: ./manage.py cleandb -h
"""
import json
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', type=str, action='store', dest='input', help='Input JSON')
        parser.add_argument('-o', type=str, action='store', dest='output', help='Output JSON')

    @staticmethod
    def get_client_secret(encrypted_client_secret):
        """Returns decrypted client secret in text."""
        if encrypted_client_secret:
            if hasattr(settings, 'OIDC_CLIENT_SECRET_KEY') and settings.OIDC_CLIENT_SECRET_KEY:
                key = settings.OIDC_CLIENT_SECRET_KEY.encode()
                try:
                    f = Fernet(key)
                    return f.decrypt(encrypted_client_secret.encode()).decode()
                except TypeError:
                    return None
                except InvalidToken:
                    print('ERROR, secret is not a valid Fernet token: %s ', encrypted_client_secret)
                    return None
        return None

    def handle(self, *args, **options):
        input_file = options['input']
        output_file = options['output']
        error = False
        if input_file and output_file:
            with open(input_file, 'r') as file:
                data = json.load(file)
            for service in data:
                if 'client_secret' in service:
                    encrypted_secret = service['client_secret']
                    decrypted_secret = self.get_client_secret(encrypted_secret)
                    if decrypted_secret:
                        service['client_secret'] = decrypted_secret
                    else:
                        error = True
            if not error:
                with open(output_file, 'w') as file:
                    json.dump(data, file,  indent=4)
