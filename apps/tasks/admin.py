from django.contrib import admin
from .models import Task
from .models import Attachment
from .models import Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_done', 'assignee', 'due_date')
    list_filter = ('is_done', 'assignee', 'due_date', 'user', 'created')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('task',)

    # TODO Show more than <Attachment object>


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
