from rr.models.serviceprovider import ServiceProvider, SPAttribute
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rr.forms.serviceprovider import BasicInformationForm
from django.utils import timezone
from rr.models.certificate import Certificate
from rr.models.contact import Contact
from rr.models.endpoint import Endpoint
from django.db.models import Q


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

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.all().order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')

    def get_context_data(self, **kwargs):
        context = super(BasicInformationView, self).get_context_data(**kwargs)
        sp = context['object']
        history = ServiceProvider.objects.filter(history=sp.pk, validated=True).last()
        if not context['object'].validated and history:
            context['attributes'] = SPAttribute.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(Q(sp=sp, end_at__gte=history.created_at) | Q(sp=sp, end_at=None))
        else:
            history = None
            context['attributes'] = SPAttribute.objects.filter(Q(sp=sp, end_at__gte=sp.updated_at) | Q(sp=sp, end_at=None))
            context['certificates'] = Certificate.objects.filter(Q(sp=sp, end_at__gte=sp.updated_at) | Q(sp=sp, end_at=None))
            context['contacts'] = Contact.objects.filter(Q(sp=sp, end_at__gte=sp.updated_at) | Q(sp=sp, end_at=None))
            context['endpoints'] = Endpoint.objects.filter(Q(sp=sp, end_at__gte=sp.updated_at) | Q(sp=sp, end_at=None))
        if history:
            context['history_object'] = history
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
    form_class = BasicInformationForm
    success_url = '#'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


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

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ServiceProvider.objects.filter(end_at=None).order_by('entity_id')
        else:
            return ServiceProvider.objects.filter(admins=self.request.user, end_at=None).order_by('entity_id')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        redirect_url = super().form_valid(form)
        sp = ServiceProvider.objects.get(pk=form.instance.pk)
        sp.validated = False
        sp.modified = True
        sp.save()
        admins = sp.admins.all()
        sp.history = sp.pk
        sp.pk = None
        sp.end_at = timezone.now()
        sp.save()
        sp.admins.set(admins)
        return redirect_url
