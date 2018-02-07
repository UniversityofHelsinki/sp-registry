from rr.models.serviceprovider import ServiceProvider, SPAttribute
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rr.forms.serviceprovider import BasicInformationForm, TechnicalInformationForm, ServiceProviderCreateForm
from django.utils import timezone
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import logging

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
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')


class BasicInformationView(DetailView):
    """
    Displays details for an invidual :model:`rr.ServiceProvider`.

    **Context**

    ``object``
        An instance of :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_detail.html`
    """
    model = ServiceProvider

    def post(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            modify_date = request.POST.get('modify_date')
            sp = self.get_object()
            if modify_date == sp.updated_at.strftime("%Y%m%d%H%M%S"):
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
            sp.validated = timezone.now()
            sp.modified = False
            sp.save()
            logger.info("SP {sp} validated by {user}".format(sp=sp, user=self.request.user))
            return HttpResponseRedirect(reverse('summary-view', args=(sp.pk,)))
        else:
            error_message = _("You should not be here.")
            logger.warning("Tried to validate without superuser access")
            return render(request, "error.html", {'error_message': error_message})

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.all().order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')

    def get_missing_data(self, sp):
        missing = []
        if sp.test or sp.production:
            if not sp.name_en and not sp.name_fi:
                missing.append(_("Service name in English or in Finnish"))
            if not sp.description_en and not sp.description_fi:
                missing.append(_("Service description in English or in Finnish"))
            if sp.production:
                if not sp.privacypolicy_en and not sp.privacypolicy_fi and sp.attributes:
                    missing.append(_("Privacy policy URL in English or in Finnish"))
            if not Certificate.objects.filter(sp=sp, end_at=None):
                missing.append(_("Certificate"))
            if not Endpoint.objects.filter(sp=sp, end_at=None, type='AssertionConsumerService'):
                missing.append(_("AssertionConsumerService endpoint"))
            if not Contact.objects.filter(sp=sp, end_at=None, type="technical"):
                missing.append(_("Technical contact"))
            if not Contact.objects.filter(sp=sp, end_at=None, type="support"):
                missing.append(_("Support contact"))

        return missing

    def get_context_data(self, **kwargs):
        context = super(BasicInformationView, self).get_context_data(**kwargs)
        sp = context['object']
        history = ServiceProvider.objects.filter(history=sp.pk).exclude(validated=None).last()
        if not context['object'].validated and history:
            context['attributes'] = SPAttribute.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
        elif context['object'].validated:
            history = None
            context['attributes'] = SPAttribute.objects.filter(Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(Q(sp=sp, end_at__gte=sp.validated) | Q(sp=sp, end_at=None))
        else:
            history = None
            context['attributes'] = SPAttribute.objects.filter(Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(Q(sp=sp, end_at__gte=sp.created_at) | Q(sp=sp, end_at=None))
        if history:
            context['history_object'] = history
        if sp.production or sp.test:
            context['missing'] = self.get_missing_data(sp)

        return context


class BasicInformationCreate(CreateView):
    """
    Displays a form for creating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_form.html`
    """
    model = ServiceProvider
    form_class = ServiceProviderCreateForm
    success_url = '#'
    template_name_suffix = '_create_form'

    def get_form_kwargs(self):
        kwargs = super(BasicInformationCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        super().form_valid(form)
        self.object.admins.add(self.request.user)
        logger.info("SP %s created by %s", self.object, self.request.user)
        return HttpResponseRedirect(reverse('summary-view', args=(self.object.pk,)))


class BasicInformationUpdate(UpdateView):
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
    template_name_suffix = '_basic_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')

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
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            if not self.request.user.is_superuser or not sp.validated:
                self.object.validated = None
            if self.request.user.is_superuser and not sp.modified:
                self.object.modified = False
            else:
                self.object.modified = True
            self.object.save()
            logger.info("SP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)


class TechnicalInformationUpdate(UpdateView):
    """
    Displays a form for updating a :model:`rr.ServiceProvider`.

    **Context**

    ``form``
        Form for :model:`rr.ServiceProvider`.

    **Template:**

    :template:`rr/serviceprovider_form.html`
    """
    model = ServiceProvider
    form_class = TechnicalInformationForm
    success_url = '#'
    template_name_suffix = '_technical_form'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')

    def get_form_kwargs(self):
        kwargs = super(TechnicalInformationUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            sp = ServiceProvider.objects.get(pk=form.instance.pk)
            # create a history copy if modifying validated SP
            if sp.validated:
                admins = sp.admins.all()
                sp.history = sp.pk
                sp.pk = None
                sp.end_at = timezone.now()
                sp.save()
                sp.admins.set(admins)
            redirect_url = super().form_valid(form)
            self.object.updated_by = self.request.user
            if not self.request.user.is_superuser or not sp.validated:
                self.object.validated = None
            if self.request.user.is_superuser and not sp.modified:
                self.object.modified = False
            else:
                self.object.modified = True
            self.object.save()
            logger.info("SP %s updated by %s", self.object, self.request.user)
            return redirect_url
        else:
            return super().form_invalid(form)