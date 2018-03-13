"""
Email notifications
"""

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging
from smtplib import SMTPException
from django.core.mail.message import BadHeaderError

logger = logging.getLogger(__name__)


def admin_notification_modified_sp(modified_sp):
    """
    Sends list of modified SPs to ADMIN_NOTIFICATION_EMAIL
    """
    if modified_sp:
        subject = render_to_string('email/admin_notification_modified_sp_subject.txt')
        message = render_to_string('email/admin_notification_modified_sp.txt',
                                   {'modified_sp': modified_sp})
        try:
            send_mail(subject, message, settings.SERVER_EMAIL, settings.ADMINS, fail_silently=False)
        except SMTPException:
            logger.error("SMTP error when sending admin notification.")
        except BadHeaderError:
            logger.error("Admin notification email contained invalid headers.")


def validation_notification(sp):
    """
    Sends validation message to SP admins.
    """
    admins = sp.admins.all()
    admin_emails = []
    for admin in admins:
        admin_emails.append(admin.email)
    if sp and admin_emails:
        subject = render_to_string('email/validation_notification_subject.txt')
        message = render_to_string('email/validation_notification.txt',
                                   {'entity_id': sp.entity_id})
        try:
            send_mail(subject, message, settings.SERVER_EMAIL, admin_emails, fail_silently=False)
        except SMTPException:
            logger.warning("SMTP error when sending validation notification.")
        except BadHeaderError:
            logger.error("Validation notification email contained invalid headers.")
