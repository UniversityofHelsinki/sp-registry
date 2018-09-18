"""
Remove historic data from database

Usage help: ./manage.py cleandb -h
"""
import logging

from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from rr.models.contact import Contact
from rr.models.serviceprovider import ServiceProvider
from rr.models.spadmin import Keystore

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-d', type=int, action='store', dest='days',
                            help='Date limit for removal (days), default 365.')
        parser.add_argument('-s', action='store_true', dest='remove_sp',
                            help='Clean service providers removed before date limit')
        parser.add_argument('-c', action='store_true', dest='remove_contact',
                            help='Clean contacts in service providers removed before time limit')
        parser.add_argument('-u', action='store_true', dest='remove_user',
                            help='Remove users without SPs and no sign in during date limit')
        parser.add_argument('-i', action='store_true', dest='remove_invite',
                            help='Remove expired invites')
        parser.add_argument('-l', action='store_true', dest='list_only',
                            help='List only, do not remove')

    def output(self, text):
        if self.list_only:
            print("(List only) " + text)
        else:
            logger.info(text)

    def handle(self, *args, **options):
        days = options['days']
        remove_sp = options['remove_sp']
        remove_contact = options['remove_contact']
        remove_user = options['remove_user']
        remove_invite = options['remove_invite']
        self.list_only = options['list_only']

        # Set date range to one year if not given
        if days is None:
            days = 365
        if days >= 0:
            remove_time = timezone.now() - relativedelta(days=days)
            if remove_sp or remove_contact:
                for provider in ServiceProvider.objects.filter(end_at__gte=remove_time,
                                                               history=None):
                    # Check for history versions
                    for sp in ServiceProvider.objects.filter(history=provider.pk):
                        if remove_sp:
                            self.output("Removing service provider (history): " + sp.entity_id)
                            if not self.list_only:
                                sp.delete()
                        elif remove_contact:
                            for contact in Contact.objects.filter(sp=sp):
                                self.output(sp.entity_id + ": Removing contact (history): "
                                            + contact.firstname + " " + contact.lastname)
                                if not self.list_only:
                                    contact.delete()
                    if remove_sp:
                        self.output("Removing service provider: " + provider.entity_id)
                        if not self.list_only:
                            provider.delete()
                    elif remove_contact:
                        for contact in Contact.objects.filter(sp=provider):
                            self.output(provider.entity_id + ": Removing contact: "
                                        + contact.firstname + " " + contact.lastname)
                            if not self.list_only:
                                contact.delete()
            if remove_user:
                # Remove users without SPs and no recent logins
                for user in User.objects.filter(last_login__gte=remove_time):
                    if not ServiceProvider.objects.filter(admins=user):
                        self.output("Removing user: " + user.username)
                        if not self.list_only:
                            user.delete()
            if remove_invite:
                expired_invites = Keystore.objects.filter(valid_until__lt=timezone.now())
                for invite in expired_invites:
                    self.output("Removing invite: " + invite.sp.entity_id + " "
                                + invite.valid_until.strftime('%Y-%m-%d') + " " + invite.email)
                    if not self.list_only:
                        invite.delete()
        else:
            print("Error: -d must be positive")
