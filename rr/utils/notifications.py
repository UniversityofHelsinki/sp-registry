"""
Email notifications
"""

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.core.mail.message import BadHeaderError
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def admin_notification_modified_sp(modified_sp, in_production, add_production, remove_production, in_test):
    """
    Sends list of modified SPs to ADMIN_NOTIFICATION_EMAIL
    """
    if (
        modified_sp
        and hasattr(settings, "ADMINS")
        and settings.ADMINS
        and hasattr(settings, "ADMIN_NOTIFICATION")
        and settings.ADMIN_NOTIFICATION
    ):
        if (
            not hasattr(settings, "ADMIN_NOTIFICATION_INCLUDE_TEST_SERVICES")
            or not settings.ADMIN_NOTIFICATION_INCLUDE_TEST_SERVICES
        ):
            in_test = None
        subject = render_to_string("email/admin_notification_modified_sp_subject.txt")
        message = render_to_string(
            "email/admin_notification_modified_sp.txt",
            {
                "modified_sp": modified_sp,
                "in_production": in_production,
                "add_production": add_production,
                "remove_production": remove_production,
                "in_test": in_test,
            },
        )
        try:
            mail_admins(subject, message)
        except SMTPException:
            logger.error("SMTP error when sending admin notification.")
        except BadHeaderError:
            logger.error("Admin notification email contained invalid headers.")


def admin_notification_created_sp(sp):
    """
    Sends message to SP admins when new service provider is created.
    """
    if (
        sp
        and hasattr(settings, "ADMINS")
        and settings.ADMINS
        and hasattr(settings, "ADMIN_NOTIFICATION")
        and settings.ADMIN_NOTIFICATION
    ):
        subject = render_to_string("email/admin_notification_created_sp_subject.txt", {"sp": sp})
        message = render_to_string("email/admin_notification_created_sp.txt", {"sp": sp})
        try:
            mail_admins(subject, message)
        except SMTPException:
            logger.error("SMTP error when sending admin notification.")
        except BadHeaderError:
            logger.error("Admin notification email contained invalid headers.")


def _render_validation_notification_message(sp):
    if sp.service_type == "saml":
        message = render_to_string("email/validation_notification_saml.txt", {"entity_id": sp.entity_id})
    elif sp.service_type == "ldap":
        message = render_to_string("email/validation_notification_ldap.txt", {"entity_id": sp.entity_id})
    else:
        message = render_to_string("email/validation_notification.txt", {"entity_id": sp.entity_id})
    return message


def validation_notification(sp):
    """
    Sends validation message to SP admins.
    """
    admin_emails = []
    if hasattr(settings, "VALIDATION_NOTIFICATION_ADMINS") and settings.VALIDATION_NOTIFICATION_ADMINS:
        admins = sp.admins.all()
        for admin in admins:
            admin_emails.append(admin.email)
    if (
        hasattr(settings, "VALIDATION_NOTIFICATION_TECHNICAL_CONTACT")
        and settings.VALIDATION_NOTIFICATION_TECHNICAL_CONTACT
    ):
        contacts = sp.contacts.filter(end_at=None, type="technical").exclude(email="")
        for contact in contacts:
            admin_emails.append(contact.email)
    if (
        hasattr(settings, "VALIDATION_NOTIFICATION_ADMINISTRATIVE_CONTACT")
        and settings.VALIDATION_NOTIFICATION_ADMINISTRATIVE_CONTACT
    ):
        contacts = sp.contacts.filter(end_at=None, type="administrative").exclude(email="")
        for contact in contacts:
            admin_emails.append(contact.email)
    # Remove duplicates emails
    admin_emails = list(set(admin_emails))
    if sp and admin_emails:
        subject = render_to_string("email/validation_notification_subject.txt")
        message = _render_validation_notification_message(sp)
        try:
            send_mail(subject, message, settings.SERVER_EMAIL, admin_emails, fail_silently=False)
        except SMTPException:
            logger.warning("SMTP error when sending validation notification.")
        except BadHeaderError:
            logger.error("Validation notification email contained invalid headers.")
