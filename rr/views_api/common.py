from django.db.models import Q

from rest_framework import mixins, viewsets


class CustomModelViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    def get_queryset(self):
        """
        Checks user access
        """
        user = self.request.user

        if user.is_superuser:
            self.queryset = self.queryset.filter(end_at=None)
        else:
            self.queryset = self.queryset.filter((Q(sp__admins=user) |
                                                  Q(sp__admin_groups__in=user.groups.all())),
                                                 end_at=None).distinct()
        return self.queryset