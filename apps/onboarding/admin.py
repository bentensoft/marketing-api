from django.contrib import admin
from .models import Channel
from .models import TemplateAssignment
from .models import Assignment


@admin.register(TemplateAssignment)
class TemplateAssignmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'order', 'created')
    list_filter = ('channel', 'created')
    fields = ('name', 'channel', 'order')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'status', 'notes')
    list_filter = ('client', 'channel')
    search_fields = ['name']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
