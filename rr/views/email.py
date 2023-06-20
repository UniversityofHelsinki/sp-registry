import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models.functions import Lower
from django.shortcuts import render
from django.utils.translation import ugettext as _

from rr.forms.email import EmailSelectForm
from rr.models.contact import Contact
from rr.models.email import Template
from rr.models.serviceprovider import ServiceProvider

logger = logging.getLogger(__name__)


@login_required
def email_list(request):
    """
    Displays a list of email addresses and
    send template email

    **Context**

    ``object_list``
        Set of email addresses.

    ``form``
        Form for selecting SPs and email types.

    ``subject``
        Message subject text

    ``message``
        Message body text

    ``errors``
        List of failed sendings

    **Template:**

    :template:`rr/email.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    emails = set()
    form = EmailSelectForm()
    subject = None
    message = None
    errors = []
    success = None
    if request.method == "POST":
        form = EmailSelectForm(request.POST)
        if form.is_valid():
            if "send_email" in request.POST:
                send = True
            else:
                send = False
            form, subject, message, success, errors = _send_emails(request, form, emails, send)
    return render(
        request,
        "rr/email.html",
        {
            "object_list": sorted(emails),
            "form": form,
            "subject": subject,
            "message": message,
            "errors": errors,
            "success": success,
        },
    )


def _send_emails(request, form, emails, send):
    subject = None
    message = None
    errors = []
    success = None
    template = request.POST.get("template", None)
    if template:
        try:
            template = Template.objects.get(pk=template)
        except Template.DoesNotExist:
            template = None
    emails = _get_addresses(form, emails)
    emails.discard("")
    if template and template.title and template.body:
        subject = template.title
        message = template.body
        if send:
            for email in emails:
                try:
                    send_mail(subject, message, settings.SERVER_EMAIL, [email], fail_silently=False)
                    logger.info("Sent email to {email} by {user}".format(email=email, user=request.user))
                except SMTPException:
                    logger.warning("Could not send invite to {email}".format(email=email))
                    errors.append(email)
            form = EmailSelectForm()
            success = _("Email have been sent")
    return form, subject, message, success, errors


def _get_addresses(form, emails):
    production_sp = form.cleaned_data["production_sp"]
    test_sp = form.cleaned_data["test_sp"]
    service_type = form.cleaned_data["service_type"]
    individual_sp = form.cleaned_data["individual_sp"]
    admin_emails = form.cleaned_data["admin_emails"]
    technical_contacts = form.cleaned_data["technical_contacts"]
    support_contacts = form.cleaned_data["support_contacts"]
    administrative_contacts = form.cleaned_data["administrative_contacts"]
    service_providers = ServiceProvider.objects.filter(end_at=None, service_type__in=service_type)
    for sp in service_providers:
        if (production_sp and sp.production) or (test_sp and sp.test) or (sp in individual_sp):
            if admin_emails:
                emails.update(sp.admins.values_list(Lower("email"), flat=True))

            if technical_contacts:
                emails.update(
                    Contact.objects.filter(sp=sp, type="technical", end_at=None).values_list(Lower("email"), flat=True)
                )
            if administrative_contacts:
                emails.update(
                    Contact.objects.filter(sp=sp, type="administrative", end_at=None).values_list(
                        Lower("email"), flat=True
                    )
                )
            if support_contacts:
                emails.update(
                    Contact.objects.filter(sp=sp, type="support", end_at=None).values_list(Lower("email"), flat=True)
                )
    return emails
