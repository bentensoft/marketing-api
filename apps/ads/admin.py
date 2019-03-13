from django.contrib import admin
from .models import Ad


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['client', 'created']
    readonly_fields = ('client', 'created')
    fields = (
        'client',
        'created',
        ('cost_adwords', 'conversions_adwords'),
        ('cost_bingads', 'conversions_bingads'),
        ('cost_facebookads', 'conversions_facebookads'),
    )
