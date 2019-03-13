from django.contrib import admin
from .models import Client


class MasterAccountsFilter(admin.SimpleListFilter):

    title = 'Show master accounts only'
    parameter_name = 'master'

    YES = '1'
    NO = '2'
    CHOICES = ((YES, 'Yes'),
               (NO, 'No'))

    def lookups(self, request, model_admin):
        return self.CHOICES

    def queryset(self, request, queryset):
        if self.value() == self.YES:
            masters = set(Client.objects.values_list('master', flat=True))
            return queryset.filter(id__in=masters)
        else:
            return queryset
