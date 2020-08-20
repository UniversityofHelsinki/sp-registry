from django.test import TestCase
from rest_framework.test import force_authenticate, APIRequestFactory


class APITestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = None
        self.object = None
        self.viewset = None

    def _test_list(self, user):
        request = self.factory.get(self.url)
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'list'})
        return view(request)

    def _test_access(self, user, pk):
        request = self.factory.get(self.url + str(pk) + '/')
        force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'get': 'retrieve'})
        return view(request, pk=pk)

    def _test_create(self, user, data):
        request = self.factory.post(self.url, data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'post': 'create'})
        return view(request)

    def _test_delete(self, user, pk):
        request = self.factory.delete(self.url + str(pk) + '/')
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'delete': 'destroy'})
        return view(request, pk=pk)

    def _test_update(self, user, data, pk):
        request = self.factory.put(self.url + str(pk) + '/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'put': 'update'})
        return view(request, pk=pk)

    def _test_patch(self, user, data, pk):
        request = self.factory.patch(self.url + str(pk) + '/', data)
        if user:
            force_authenticate(request, user=user)
        view = self.viewset.as_view(actions={'patch': 'partial_update'})
        return view(request, pk=pk)
