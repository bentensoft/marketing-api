from django.contrib import admin
from .filters import MasterAccountsFilter
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_enabled', 'master',
                    'adwords_id', 'bingads_id', 'facebookads_id']
    list_filter = ['is_enabled', MasterAccountsFilter]
    search_fields = ['name', 'adwords_id', 'bingads_id', 'facebookads_id']
