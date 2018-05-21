import logging
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from rr.models.serviceprovider import ServiceProvider
from rr.models.contact import Contact
from rr.forms.email import EmailSelectForm
from django.core.mail import send_mail
from django.conf import settings
from smtplib import SMTPException
from rr.models.email import Template

logger = logging.getLogger(__name__)


@login_required
def email_list(request):
    """
    Displays a list of email addresses and
    send template emails

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
    form = EmailSelectForm()
    emails = set()
    subject = None
    message = None
    errors = []
    success = None
    if request.method == "POST":
        form = EmailSelectForm(request.POST)
        if "send_email" in request.POST:
            send = True
        else:
            send = False
        if form.is_valid():
            production_sp = form.cleaned_data['production_sp']
            test_sp = form.cleaned_data['test_sp']
            individual_sp = form.cleaned_data['individual_sp']
            admin_emails = form.cleaned_data['admin_emails']
            technical_contacts = form.cleaned_data['technical_contacts']
            support_contacts = form.cleaned_data['support_contacts']
            administrative_contacts = form.cleaned_data['administrative_contacts']
            template = request.POST.get('template', None)
            if template:
                try:
                    template = Template.objects.get(pk=template)
                except Template.DoesNotExist:
                    template = None
            service_providers = ServiceProvider.objects.filter(end_at=None)
            for sp in service_providers:
                if (production_sp and sp.production) or (test_sp and sp.test) or (str(sp.pk) in individual_sp):
                    if admin_emails:
                        emails.update(sp.admins.values_list(Lower('email'), flat=True))
                    if technical_contacts:
                        emails.update(Contact.objects.filter(sp=sp, type="technical", end_at=None).values_list(Lower('email'), flat=True))
                    if administrative_contacts:
                        emails.update(Contact.objects.filter(sp=sp, type="administrative", end_at=None).values_list(Lower('email'), flat=True))
                    if support_contacts:
                        emails.update(Contact.objects.filter(sp=sp, type="support", end_at=None).values_list(Lower('email'), flat=True))
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
                    success = _("Emails have been sent")
    return render(request, "rr/email.html", {'object_list': sorted(emails),
                                             'form': form,
                                             'subject': subject,
                                             'message': message,
                                             'errors': errors,
                                             'success': success})
    