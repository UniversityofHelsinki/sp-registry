import logging

from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail.message import BadHeaderError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.context import Context
from django.template.engine import Engine
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext as _

from rr.forms.spadmin import SPAdminForm
from rr.models.email import Template
from rr.models.serviceprovider import ServiceProvider
from rr.models.spadmin import Keystore
from rr.utils.serviceprovider import get_service_provider


logger = logging.getLogger(__name__)


def get_hostname(request):
    """
    Create URI with scheme and hostname
    """
    if request.is_secure():
        return 'https://' + request.META.get('HTTP_HOST', '')
    else:
        return 'http://' + request.META.get('HTTP_HOST', '')


def get_activation_link(request, key):
    """
    Create invite activation link URI
    """
    return get_hostname(request) + "/invite/?key=" + key.activation_key


def render_email(request, text, key):
    """
    Render invite email context from template object.
    """
    context = Engine().from_string(text).render(Context(
            {'creator': key.creator.first_name + " " + key.creator.last_name,
             'entity_id': key.sp.entity_id,
             'activation_link': get_activation_link(request, key),
             'valid_until': key.valid_until}))
    return context


def create_invite_email(request, key, template):
    """
    Return subject and message for email, rendered from template if found.
    Return error if action link is not found from email.
    """
    if template:
        try:
            template = Template.objects.get(pk=template)
        except Template.DoesNotExist:
            template = None
    if template:
        subject = render_email(request, template.title, key)
        message = render_email(request, template.body, key)
    else:
        subject = render_to_string('email/activation_email_subject.txt')
        message = render_to_string(
                'email/activation_email.txt',
                {'creator': key.creator.first_name + " " + key.creator.last_name,
                 'entity_id': key.sp.entity_id,
                 'activation_link': get_activation_link(request, key),
                 'valid_until': key.valid_until.strftime("%d.%m.%Y")})
    if get_activation_link(request, key) not in message:
        error = _("Template is missing activation link. "
                  "Please include {{ activation_link }} to message.")
    else:
        error = None
    return subject, message, error


@login_required
def admin_list(request, pk):
    """
    Displays a lists of :model:`auth.User` and :model:`rr.Keystore`
    linked to :model:`rr.ServiceProvider`.

    **Context**

    ``object_list``
        List of :model:`rr.Keystore`.

    ``form``
        Form for sending an invitation

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/admin.html`
    """
    sp = get_service_provider(pk, request.user)
    form = SPAdminForm(superuser=request.user.is_superuser)
    subject = None
    message = None
    error = None
    if request.method == "POST":
        if "add_invite" in request.POST:
            form, subject, message, error = _create_invite(request, sp, True)
        elif "show_message" in request.POST:
            form, subject, message, error = _create_invite(request, sp, False)
        elif "remove_invite" in request.POST:
            _remove_invites(request, sp)
        elif "remove_admin" in request.POST:
            remove_self = _remove_admins(request, sp)
            if remove_self:
                return HttpResponseRedirect(reverse('serviceprovider-list'))
    invites = Keystore.objects.filter(sp=sp)
    return render(request, "rr/spadmin.html", {'object_list': invites,
                                               'form': form,
                                               'object': sp,
                                               'subject': subject,
                                               'message': message,
                                               'error': error})


def _create_invite(request, sp, send):
    form = SPAdminForm(request.POST, superuser=request.user.is_superuser)
    subject = None
    message = None
    error = None
    if form.is_valid():
        email = form.cleaned_data['email']
        template = request.POST.get('template', None)
        key = Keystore.objects.create_key(sp=sp, creator=request.user, email=email)
        subject, message, error = create_invite_email(request, key, template)
        if send and not error:
            try:
                send_mail(subject, message, settings.SERVER_EMAIL, [email],
                          fail_silently=False)
                logger.info("Invite for {sp} sent to {email} by {user}"
                            .format(sp=sp, email=email, user=request.user))
                form = SPAdminForm(superuser=request.user.is_superuser)
                subject = None
                message = None
                messages.add_message(request, messages.INFO,
                                     _('Invite sent to ') + email)
            except SMTPException:
                logger.warning("Could not send invite to {email}"
                               .format(email=email))
                error = _("Could not send email.")
                key.delete()
            except BadHeaderError:
                logger.warning("Email from {user} contained invalid headers."
                               .format(user=request.user))
                error = _("Invalid header found, could not send email.")
                key.delete()
        else:
            key.delete()
    return form, subject, message, error


def _remove_invites(request, sp):
    for key, value in request.POST.dict().items():
        if value == "on":
            invite = Keystore.objects.filter(pk=key).first()
            if invite and invite.sp == sp:
                logger.info("Invite for {email} to {sp} deleted by {user}"
                            .format(email=invite.email, sp=sp, user=request.user))
                messages.add_message(request, messages.INFO,
                                     _('Invite removed for email ') + invite.email)
                invite.delete()
            else:
                messages.add_message(request, messages.INFO,
                                     _('Invite already used or removed'))


def _remove_admins(request, sp):
    removed_self = False
    for key, value in request.POST.dict().items():
        if value == "on":
            admin = User.objects.get(pk=key)
            logger.info("Admin {admin} removed from {sp} by {user}"
                        .format(admin=admin, sp=sp, user=request.user))
            messages.add_message(request, messages.INFO,
                                 _('Admin removed: ') + admin.username)
            sp.admins.remove(admin)
            try:
                if request.user.is_superuser:
                    sp = ServiceProvider.objects.get(pk=sp.pk, end_at=None)
                else:
                    sp = ServiceProvider.objects.get(pk=sp.pk, admins=request.user,
                                                     end_at=None)
            except ServiceProvider.DoesNotExist:
                removed_self = True
    return removed_self


@login_required
def activate_key(request, invite_key=""):
    """
    Activates an :model:`rr.Keystore' adding
    :model:`auth.User` to :model:`rr.ServiceProvider`.

    Redirects to summary-view.
    """
    get_key = request.GET.get('key', '')
    if get_key:
        invite_key = get_key
    sp = Keystore.objects.activate_key(user=request.user,
                                       key=invite_key)
    if sp:
        return HttpResponseRedirect(reverse('summary-view', args=(sp,)))
    else:
        error_message = _("Activation key does not match")
        return render(request, "error.html", {'error_message': error_message})
