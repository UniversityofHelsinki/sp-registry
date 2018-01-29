from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from rr.models.serviceprovider import ServiceProvider
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KeystoreManager(models.Manager):
    """
    Manager for Keystore
    """
    def create_key(self, sp, creator, email, hostname):
        """
        Creates invitation key for a SP
        Sends it to user by email, using templates/email to generate content
        - sp is Service Provider object invite is for
        - creator is User object for user creating a key
        - email is email address where invitation is sent
        """
        import hashlib
        import random
        from dateutil.relativedelta import relativedelta
        date = timezone.now() + relativedelta(months=1)
        activation_key = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
        self.create(sp=sp, creator=creator, activation_key=activation_key, email=email, valid_until=date)
        subject = render_to_string('email/activation_email_subject.txt')
        message = render_to_string('email/activation_email.txt',
                                   {'creator': creator.first_name + " " + creator.last_name,
                                    'sp': sp.entity_id,
                                    'activation_key': activation_key,
                                    'valid': date.date,
                                    'hostname': hostname})
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return activation_key

    def activate_key(self, user, key):
        """
        Add user to SP admins if key matches
        """
        try:
            keystore = self.get(activation_key=key)
        except self.model.DoesNotExist:
            logger.info("Tried to access invalid invite key")
            return False
        if timezone.now().date() > keystore.valid_until:
            logger.info("Tried to access old invite key")
            keystore.delete()
            return False
        keystore.sp.admins.add(user)
        logger.info("Invite key for %s was activated by %s", keystore.sp, user)
        sp = keystore.sp.pk
        keystore.delete()
        return sp


class Keystore(models.Model):
    """
    Stores a single invite, related to :model:`rr.ServiceProvider` and :model:`auth.User`
    """
    sp = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, verbose_name=_('Creator'))
    activation_key = models.CharField(max_length=40, verbose_name=_('Activation key'))
    valid_until = models.DateField(verbose_name=_('Valid until date'))
    email = models.EmailField(verbose_name=_('Email address'))

    objects = KeystoreManager()
