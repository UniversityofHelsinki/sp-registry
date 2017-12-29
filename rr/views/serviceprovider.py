from rr.models.serviceprovider import ServiceProvider
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rr.forms.serviceprovider import BasicInformationForm


class ServiceProviderList(ListView):
    model = ServiceProvider

    def get_queryset(self):
        return ServiceProvider.objects.filter(admins=self.request.user).order_by('entity_id')


class BasicInformationView(DetailView):
    model = ServiceProvider

    def get_queryset(self):
        return ServiceProvider.objects.filter(admins=self.request.user).order_by('entity_id')


class BasicInformationCreate(CreateView):
    model = ServiceProvider
    form_class = BasicInformationForm
    success_url = '#'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class BasicInformationUpdate(UpdateView):
    model = ServiceProvider
    form_class = BasicInformationForm
    success_url = '#'

    def get_queryset(self):
        return ServiceProvider.objects.filter(admins=self.request.user).order_by('entity_id')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
