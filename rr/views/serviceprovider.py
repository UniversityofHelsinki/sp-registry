import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from rr.forms.serviceprovider import BasicInformationForm, SamlTechnicalInformationForm
from rr.forms.serviceprovider import OidcServiceProviderCreateForm, OidcTechnicalInformationForm
from rr.forms.serviceprovider import SamlServiceProviderCreateForm, LdapServiceProviderCreateForm
from rr.forms.serviceprovider import ServiceProviderValidationForm, LdapTechnicalInformationForm

from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from rr.models.redirecturi import RedirectUri
from rr.models.serviceprovider import ServiceProvider, SPAttribute, new_ldap_entity_id_from_name
from rr.models.testuser import update_entity_ids
from rr.models.usergroup import UserGroup
from rr.utils.notifications import validation_notification, admin_notification_created_sp

logger = logging.getLogger(__name__)


class ServiceProviderList(ListView):
    """
    Displays a list of :model:`rr.ServiceProvider` which
    user has access.


    **Context**

    ``object_list``
        List of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_list.html`
    """
    model = ServiceProvider

    def get_queryset(self):
        if not settings.ACTIVATE_SAML:
            return ServiceProvider.objects.none()
        if self.request.user and self.request.user.is_superuser:
            return ServiceProvider.objects.filter(
                end_at=None, service_type="saml").order_by('-modified', '-production', '-test', 'entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None,
                                                  service_type="saml").order_by('entity_id')

    def get_context_data(self, **kwargs):
        context = super(ServiceProviderList, self).get_context_data(**kwargs)
        if not settings.ACTIVATE_LDAP:
            context['ldap_providers'] = ServiceProvider.objects.none()
        elif self.request.user.is_superuser:
            context['ldap_providers'] = ServiceProvider.objects.filter(
                end_at=None, service_type="ldap").order_by('-modified', '-production', 'entity_id')
        else:
            context['ldap_providers'] = ServiceProvider.objects.filter(
                admins=self.request.user, end_at=None, service_type="ldap").order_by('entity_id')

        if not settings.ACTIVATE_OIDC:
            context['oidc_providers'] = ServiceProvider.objects.none()
        elif self.request.user.is_superuser:
            context['oidc_providers'] = ServiceProvider.objects.filter(
                end_at=None, service_type="oidc").order_by('-modified', '-production', 'entity_id')
        else:
            context['oidc_providers'] = ServiceProvider.objects.filter(
                admins=self.request.user, end_at=None, service_type="oidc").order_by('entity_id')

        context['activate_saml'] = settings.ACTIVATE_SAML
        context['activate_ldap'] = settings.ACTIVATE_LDAP
        context['activate_oidc'] = settings.ACTIVATE_OIDC
        return context


class BasicInformationView(DetailView):
    """
    Displays details for an individual :model:`rr.ServiceProvider`.

    **Context**

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_detail.html`
    """
    model = ServiceProvider

    @staticmethod
    def _validate_linked_models(sp):
        for attribute in SPAttribute.objects.filter(sp=sp, end_at=None, validated=None):
            attribute.validated = timezone.now()
            attribute.save()
        for certificate in Certificate.objects.filter(sp=sp, end_at=None, validated=None):
            certificate.validated = timezone.now()
            certificate.save()
        for contact in Contact.objects.filter(sp=sp, end_at=None, validated=None):
            contact.validated = timezone.now()
            contact.save()
        for endpoint in Endpoint.objects.filter(sp=sp, end_at=None, validated=None):
            endpoint.validated = timezone.now()
            endpoint.save()
        for usergroup in UserGroup.objects.filter(sp=sp, end_at=None, validated=None):
            usergroup.validated = timezone.now()
            usergroup.save()
        for redirecturi in RedirectUri.objects.filter(sp=sp, end_at=None, validated=None):
            redirecturi.validated = timezone.now()
            redirecturi.save()

    def post(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            modified_date = request.POST.get('modified_date')
            no_email = request.POST.get('no_email')
            sp = self.get_object()
            if modified_date == sp.updated_at.strftime("%Y%m%d%H%M%S%f"):
                self._validate_linked_models(sp)
                sp.validated = timezone.now()
                sp.modified = False
                sp.save()
                if not no_email:
                    validation_notification(sp)
                logger.info("SP {sp} validated by {user}".format(sp=sp, user=self.request.user))
                messages.add_message(request, messages.INFO, _('Changes validated.'))
            return HttpResponseRedirect(reverse('summary-view', args=(sp.pk,)))
        else:
            error_message = _("You should not be here.")
            logger.warning("Tried to validate without superuser access")
            return render(request, "error.html", {'error_message': error_message})

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.all().order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user,
                                                  end_at=None).order_by('entity_id')


    @staticmethod
    def _get_missing_saml_data(sp, missing):
        if not sp.privacypolicy_en and not sp.privacypolicy_fi and sp.attributes:
            url = reverse("basicinformation-update", args=[sp.pk])
            msg = _("Privacy policy URL in English or in Finnish")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if not Certificate.objects.filter(sp=sp, end_at=None):
            url = reverse("certificate-list", args=[sp.pk])
            msg = _("Certificate")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if not Endpoint.objects.filter(sp=sp, end_at=None,
                                       type='AssertionConsumerService'):
            url = reverse("endpoint-list", args=[sp.pk])
            msg = _("AssertionConsumerService endpoint")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        return missing

    @staticmethod
    def _get_missing_oidc_data(sp, missing):
        if not RedirectUri.objects.filter(sp=sp, end_at=None):
            url = reverse("redirecturi-list", args=[sp.pk])
            msg = _("Redirect URI")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        return missing

    def _get_missing_data(self, sp):
        missing = []
        if not sp.name_en and not sp.name_fi:
            url = reverse("basicinformation-update", args=[sp.pk])
            msg = _("Service name in English or in Finnish")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if not sp.description_en and not sp.description_fi:
            url = reverse("basicinformation-update", args=[sp.pk])
            msg = _("Service description in English or in Finnish")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if not sp.application_portfolio:
            url = reverse("basicinformation-update", args=[sp.pk])
            msg = _("Application portfolio URL")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if not Contact.objects.filter(sp=sp, end_at=None, type="technical"):
            url = reverse("contact-list", args=[sp.pk])
            msg = _("Technical contact")
            missing.append("<a href='" + url + "'>" + msg + "</a>")
        if sp.service_type == "saml":
            missing = self._get_missing_saml_data(sp, missing)
        elif sp.service_type == "oidc":
            missing = self._get_missing_oidc_data(sp, missing)
        return missing

    def get_context_data(self, **kwargs):
        context = super(BasicInformationView, self).get_context_data(**kwargs)
        sp = context['object']
        history = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
        if not context['object'].validated and history:
            context['attributes'] = SPAttribute.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['usergroups'] = UserGroup.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['redirecturis'] = RedirectUri.objects.filter(
                Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
        elif context['object'].validated:
            history = None
            context['attributes'] = SPAttribute.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['usergroups'] = UserGroup.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['redirecturis'] = RedirectUri.objects.filter(
                Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
        else:
            history = None
            context['attributes'] = SPAttribute.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['usergroups'] = UserGroup.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['redirecturis'] = RedirectUri.objects.filter(
                Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
        if history:
            context['history_object'] = history
        if sp.production:
            context['missing'] = self._get_missing_data(sp)
        if self.request.user.is_superuser and sp.modified:
            context['form'] = ServiceProviderValidationForm(
                modified_date=sp.updated_at.strftime("%Y%m%d%H%M%S%f"))
        else:
            context['form'] = None
        return context


class SamlServiceProviderCreate(CreateView):
    """
    Displays a form for creating a SAML :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_saml_create_form.html`
    """
    model = ServiceProvider
    form_class = SamlServiceProviderCreateForm
    success_url = '#'
    template_name_suffix = '_saml_create_form'

    def get_form_kwargs(self):
        kwargs = super(SamlServiceProviderCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.service_type = "saml"
        super().form_valid(form)
        self.object.admins.add(self.request.user)
        logger.info("SAML service %s created by %s", self.object, self.request.user)
        admin_notification_created_sp(self.object)
        return HttpResponseRedirect(reverse('summary-view', args=(self.object.pk,)))


class LdapServiceProviderCreate(CreateView):
    """
    Displays a form for creating a LDAP :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_ldap_create_form.html`
    """
    model = ServiceProvider
    form_class = LdapServiceProviderCreateForm
    success_url = '#'
    template_name_suffix = '_ldap_create_form'

    def get_form_kwargs(self):
        kwargs = super(LdapServiceProviderCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.service_type = "ldap"
        form.instance.entity_id = new_ldap_entity_id_from_name(form.instance.name_fi)
        super().form_valid(form)
        self.object.admins.add(self.request.user)
        logger.info("LDAP service %s created by %s", self.object, self.request.user)
        admin_notification_created_sp(self.object)
        return HttpResponseRedirect(reverse('summary-view', args=(self.object.pk,)))


class OidcServiceProviderCreate(CreateView):
    """
    Displays a form for creating a OIDC :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_oidc_create_form.html`
    """
    model = ServiceProvider
    form_class = OidcServiceProviderCreateForm
    success_url = '#'
    template_name_suffix = '_oidc_create_form'

    def get_form_kwargs(self):
        kwargs = super(OidcServiceProviderCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.service_type = "oidc"
        super().form_valid(form)
        self.object.admins.add(self.request.user)
        self.object.generate_client_secret()
        logger.info("OIDC service %s created by %s", self.object, self.request.user)
        admin_notification_created_sp(self.object)
        return HttpResponseRedirect(reverse('summary-view', args=(self.object.pk,)))


class BasicInformationUpdate(SuccessMessageMixin, UpdateView):
    """
    Displays a form for updating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_form.html`
    """
    model = ServiceProvider
    form_class = BasicInformationForm
    success_url = '#'
    success_message = _("Form successfully saved")
    template_name_suffix = '_basic_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user,
                                                  end_at=None).order_by('entity_id')

    def get_form_kwargs(self):
        kwargs = super(BasicInformationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            sp = ServiceProvider.objects.get(pk=form.instance.pk)
            # create a history copy if modifying validated SP
            if sp.validated:
                admins = sp.admins.all()
                nameidformat = sp.nameidformat.all()
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
                sp.nameidformat.set(nameidformat)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            self.object.validated = None
            self.object.save_modified()
            logger.info("SP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)


class SamlTechnicalInformationUpdate(SuccessMessageMixin, UpdateView):
    """
    Displays a form for updating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_saml_technical_form.html`
    """
    model = ServiceProvider
    form_class = SamlTechnicalInformationForm
    success_url = '#'
    success_message = _("Form successfully saved")
    template_name_suffix = '_saml_technical_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None, service_type="saml").order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, service_type="saml",
                                                  end_at=None).order_by('entity_id')

    def get_form_kwargs(self):
        kwargs = super(SamlTechnicalInformationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            sp = ServiceProvider.objects.get(pk=form.instance.pk)
            # create a history copy if modifying validated SP
            if sp.validated:
                admins = sp.admins.all()
                nameidformat = sp.nameidformat.all()
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
                sp.nameidformat.set(nameidformat)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            self.object.validated = None
            # Update entity_ids for testusers if it has changed
            if 'entity_id' in form.changed_data:
                update_entity_ids(self.object)
            self.object.save_modified()
            logger.info("SP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)


class LdapTechnicalInformationUpdate(SuccessMessageMixin, UpdateView):
    """
    Displays a form for updating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_ldap_technical_form.html`
    """
    model = ServiceProvider
    form_class = LdapTechnicalInformationForm
    success_url = '#'
    success_message = _("Form successfully saved")
    template_name_suffix = '_ldap_technical_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None,
                                                  service_type="ldap").order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, service_type="ldap",
                                                  end_at=None).order_by('entity_id')

    def get_form_kwargs(self):
        kwargs = super(LdapTechnicalInformationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            sp = ServiceProvider.objects.get(pk=form.instance.pk)
            # create a history copy if modifying validated SP
            if sp.validated:
                admins = sp.admins.all()
                nameidformat = sp.nameidformat.all()
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
                sp.nameidformat.set(nameidformat)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            self.object.validated = None
            self.object.save_modified()
            logger.info("SP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)


class OidcTechnicalInformationUpdate(SuccessMessageMixin, UpdateView):
    """
    Displays a form for updating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_oidc_technical_form.html`
    """
    model = ServiceProvider
    form_class = OidcTechnicalInformationForm
    success_url = '#'
    success_message = _("Form successfully saved")
    template_name_suffix = '_oidc_technical_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None, service_type="oidc").order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, service_type="oidc",
                                                  end_at=None).order_by('entity_id')

    def get_form_kwargs(self):
        kwargs = super(OidcTechnicalInformationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):

        if form.has_changed():
            sp = ServiceProvider.objects.get(pk=form.instance.pk)
            # create a history copy if modifying validated SP
            if sp.validated:
                admins = sp.admins.all()
                grant_types = sp.grant_types.all()
                response_types = sp.response_types.all()
                oidc_scopes = sp.oidc_scopes.all()
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
                sp.grant_types.set(grant_types)
                sp.response_types.set(response_types)
                sp.oidc_scopes.set(oidc_scopes)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            self.object.validated = None
            # Update entity_ids for testusers if it has changed
            if 'entity_id' in form.changed_data:
                update_entity_ids(self.object)
            if form.cleaned_data['reset_client_secret']:
                client_secret = self.object.generate_client_secret()
                if client_secret:
                    logger.info("Client secret generated for {sp} by {user}".format(sp=sp, user=self.request.user))
                    messages.add_message(self.request, messages.INFO, _('Client secret generated.'))
                else:
                    messages.add_message(self.request, messages.ERROR,
                        _('Unable to generate a client secret. Usually this means incorrect server configuration.'))
            if form.cleaned_data['remove_client_secret']:
                self.object.encrypted_client_secret = ""
                logger.info("Client secret removed from {sp} by {user}".format(sp=sp, user=self.request.user))
                messages.add_message(self.request, messages.INFO, _('Client secret removed.'))
            self.object.save_modified()
            logger.info("RP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)


class ServiceProviderDelete(SuccessMessageMixin, DeleteView):
    model = ServiceProvider
    success_url = reverse_lazy('serviceprovider-list')
    success_message = _("Service deleted.")

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user,
                                                  end_at=None).order_by('entity_id')

    def delete(self, request, *args, **kwargs):
        """
        Update regular delete function to set end_at null instead.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        allow_delete = True
        if self.object.production:
            allow_delete = False
        if not self.object.validated:
            history = ServiceProvider.objects.filter(history=self.object.pk).exclude(validated=None).last()
            if history and history.production:
                allow_delete = False
        if allow_delete:
            self.object.end_at = timezone.now()
            self.object.save()
            messages.add_message(request, messages.INFO, self.success_message)
        else:
            messages.add_message(request, messages.ERROR, _("Service removal is not allowed for production services."))
            success_url = reverse_lazy('summary-view', kwargs={'pk': self.object.pk})
        return HttpResponseRedirect(success_url)


class SAMLAdminList(ListView):
    """
    Displays a list of SAML :model:`rr.ServiceProvider` where
    special configurations are enabled

    **Context**

    ``object_list``
        List of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_saml_admin_list.html`
    """
    model = ServiceProvider
    template_name_suffix = '_saml_admin_list'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(service_type="saml", end_at=None).order_by('entity_id')
        else:
            raise PermissionDenied
