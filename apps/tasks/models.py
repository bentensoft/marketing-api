from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_extensions.db.models import TimeStampedModel
from base.tasks import send_email


class Task(TimeStampedModel):
    """Tasks item"""

    user = models.ForeignKey('auth.User', verbose_name='User',
                             on_delete=models.SET_NULL, null=True)
    name = models.TextField('Name', null=True)
    body = models.TextField('Body', blank=True, null=True)
    client = models.ForeignKey('clients.Client', blank=True, null=True,
                               on_delete=models.SET_NULL,
                               related_name='tasks')
    is_done = models.BooleanField('Is Done', default=False, blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    assignee = models.ForeignKey('auth.User', verbose_name='Assignee',
                                 blank=True, null=True,
                                 related_name='assignees')
    watchers = models.ManyToManyField('auth.User', verbose_name='Watchers',
                                      blank=True, related_name='watchers')
    is_recurring = models.BooleanField('Make the task recurring',
                                       default=False)

    EVERY_MONDAY = 'monday'
    EVERY_TUESDAY = 'tuesday'
    EVERY_WEDNESDAY = 'wednesday'
    EVERY_THURSDAY = 'thursday'
    EVERY_FRIDAY = 'friday'
    EVERY_SATURDAY = 'saturday'
    EVERY_SUNDAY = 'sunday'
    EVERY_CHOICES = (
        (EVERY_MONDAY, 'Monday'),
        (EVERY_TUESDAY, 'Tuesday'),
        (EVERY_WEDNESDAY, 'Wednesday'),
        (EVERY_THURSDAY, 'Thursday'),
        (EVERY_FRIDAY, 'Friday'),
        (EVERY_SATURDAY, 'Saturday'),
        (EVERY_SUNDAY, 'Sunday')
    )
    every = models.CharField('Occur every', choices=EVERY_CHOICES,
                             blank=True, null=True, max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tasks'
        ordering = ['-due_date', '-created']


class Attachment(TimeStampedModel):
    task = models.ForeignKey('Task', related_name='attachments', null=True)
    file = models.FileField(upload_to='attachments/', null=True)


class Comment(TimeStampedModel):
    """Comments for tasks"""
    task = models.ForeignKey('Task', related_name='comments')
    author = models.ForeignKey('auth.User', related_name='comments')
    text = models.TextField()

    def __str__(self):
        return '%s: %s' % (self.task, self.author)

    class Meta:
        ordering = ['created']


@receiver(post_save, sender=Task)
def notify_by_email(sender, instance, created, **kwargs):
    message = """
    Task: {task}
    Due Date: {due_date}
    """.format(task=instance.name, due_date=instance.due_date)
    mail_kwargs = {
        'subject': 'APP-TASK: %s' % instance.client,
        'message': message, 'to': [instance.assignee.email]}

    if created:
        send_email.apply_async(kwargs=mail_kwargs)

    for watcher in instance.watchers.all():
        mail_kwargs['to'] = [watcher.email]
        send_email.apply_async(kwargs=mail_kwargs)
