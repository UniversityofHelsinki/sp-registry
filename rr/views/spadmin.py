from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from rr.models.spadmin import Keystore
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rr.models.serviceprovider import ServiceProvider
from rr.forms.spadmin import SPAdminForm
from django.http.response import Http404
from django.contrib.auth.models import User
import logging
from rr.models.email import Template
from django.template.loader import render_to_string
from django.template.engine import Engine
from django.template.context import Context
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger(__name__)


def get_hostname(request):
    if request.is_secure():
        return 'https://' + request.META.get('HTTP_HOST', '')
    else:
        return 'http://' + request.META.get('HTTP_HOST', '')


def get_activation_link(request, key):
    return get_hostname(request) + "/invite/" + key.activation_key


def render_email(request, text, key):
    context = Engine().from_string(text).render(Context({'creator': key.creator.first_name + " " + key.creator.last_name,
                                                         'entity_id': key.sp.entity_id,
                                                         'activation_link': get_activation_link(request, key),
                                                         'valid_until': key.valid_until,
                                                         }))
    return context


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
    try:
        if request.user.is_superuser:
            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
        else:
            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
    except ServiceProvider.DoesNotExist:
        logger.debug("Tried to access unauthorized service provider")
        raise Http404("Service provider does not exist")
    form = SPAdminForm(superuser=request.user.is_superuser)
    subject = None
    message = None
    error = None
    if request.method == "POST":
        if "add_invite" in request.POST or "show_message" in request.POST:
            if "add_invite" in request.POST:
                send = True
            else:
                send = False
            print(send)
            form = SPAdminForm(request.POST, superuser=request.user.is_superuser)
            if form.is_valid():
                email = form.cleaned_data['email']
                template = request.POST.get('template', None)
                print(template)
                if template:
                    try:
                        template = Template.objects.get(pk=template)
                    except Template.DoesNotExist:
                        template = None
                key = Keystore.objects.create_key(sp=sp, creator=request.user, email=email)
                if template:
                    print(template.title)
                    subject = render_email(request, template.title, key)
                    print(subject)
                    message = render_email(request, template.body, key)
                else:
                    subject = render_to_string('email/activation_email_subject.txt')
                    message = render_to_string('email/activation_email.txt',
                                               {'creator': key.creator.first_name + " " + key.creator.last_name,
                                                'entity_id': key.sp.entity_id,
                                                'activation_link': get_activation_link(request, key),
                                                'valid_until': key.valid_until.strftime("%d.%m.%Y")})
                if get_activation_link(request, key) not in message:
                   send = False
                   error = _("Template is missing activation link. Please include {{ activation_link }} to message.")
                if send:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                    logger.info("Invite for {sp} sent to {email} by {user}".format(sp=sp, email=email, user=request.user))
                    form = SPAdminForm(superuser=request.user.is_superuser)
                    subject = None
                    message = None
                else:
                    key.delete()
        elif "remove_invite" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    invite = Keystore.objects.get(pk=key)
                    if invite.sp == sp:
                        logger.info("Invite for {email} to {sp} deleted by {user}".format(email=invite.email, sp=sp, user=request.user))
                        invite.delete()
        elif "remove_admin" in request.POST:
            for key, value in request.POST.dict().items():
                if value == "on":
                    admin = User.objects.get(pk=key)
                    logger.info("Admin {admin} removed from {sp} by {user}".format(admin=admin, sp=sp, user=request.user))
                    sp.admins.remove(admin)
                    try:
                        if request.user.is_superuser:
                            sp = ServiceProvider.objects.get(pk=pk, end_at=None)
                        else:
                            sp = ServiceProvider.objects.get(pk=pk, admins=request.user, end_at=None)
                    except ServiceProvider.DoesNotExist:
                        return HttpResponseRedirect(reverse('serviceprovider-list'))
    invites = Keystore.objects.filter(sp=sp)
    return render(request, "rr/spadmin.html", {'object_list': invites,
                                               'form': form,
                                               'object': sp,
                                               'subject': subject,
                                               'message': message,
                                               'error': error})


@login_required
def activate_key(request, invite_key=""):
    """
    Activates an :model:`rr.Keystore' adding
    :model:`auth.User` to :model:`rr.ServiceProvider`.

    Redirects to summary-view.
    """

    sp = Keystore.objects.activate_key(user=request.user,
                                       key=invite_key)
    if sp:
        return HttpResponseRedirect(reverse('summary-view', args=(sp,)))
    else:
        error_message = _("Activation key does not match")
        return render(request, "error.html", {'error_message': error_message})
