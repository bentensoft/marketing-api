from django.contrib import admin
from .models import Ngram


@admin.register(Ngram)
class NgramAdmin(admin.ModelAdmin):
    list_display = ('client', 'created', 'word', 'cost', 'conversions')
    list_filter = ('client',)
