from rr.models.serviceprovider import ServiceProvider
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rr.forms.serviceprovider import BasicInformationForm
from django.utils import timezone


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
        sp = ServiceProvider.objects.get(pk=form.instance.pk)
        admins = sp.admins.all()
        sp.pk = None
        sp.end_at = timezone.now()
        sp.save()
        sp.admins.set(admins)
        return super().form_valid(form)
