from django.db import models
from django.contrib.admin.models import LogEntry, ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_extensions.db.models import TimeStampedModel
from clients.models import Client


class Channel(TimeStampedModel):
    """Channel where task is required"""
    name = models.CharField('Name', max_length=255)
    logo = models.ImageField('Logo', upload_to='channel_logos/', blank=True)
    order = models.PositiveIntegerField('Order', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'channels'
        ordering = ('order',)


class TemplateAssignment(TimeStampedModel):
    """
    Task that will be part of the predefined list of tasks for the
    user
    """
    YES = 'yes'
    NO = 'no'
    NA = 'n/a'
    WAITING = 'waiting'
    STATUS_CHOICES = (
        (YES, 'Yes'),
        (NO, 'No'),
        (NA, 'N/A'),
        (WAITING, 'Waiting on Client'),
    )

    channel = models.ForeignKey(Channel, related_name='template_assignments',
                                null=True)
    name = models.CharField('Name', max_length=255, null=True)
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True,
                              max_length=255)
    order = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        created = False
        if not self.pk:
            created = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'template_assignments'
        ordering = ('order',)


@receiver(post_save, sender=TemplateAssignment)
def autoadd(sender, instance, created, **kwargs):
    if created:
        clients = Client.objects.all()
        for client in clients:
            assignment = Assignment(
                client=client,
                channel=instance.channel,
                name=instance.name,
            )
            assignment.save()


class Assignment(TimeStampedModel):
    """Task for real usage by team and clients"""
    client = models.ForeignKey('clients.Client', verbose_name='Client',
                               related_name='assignments', null=True)
    channel = models.ForeignKey(Channel, related_name='assignments', null=True,
                                db_index=True)
    name = models.CharField('Setup Assignment', max_length=255, null=True)
    notes = models.TextField('Notes', blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    YES = 'yes'
    NO = 'no'
    NA = 'n/a'
    WAITING = 'waiting'
    STATUS_CHOICES = (
        (YES, 'Yes'),
        (NO, 'No'),
        (NA, 'N/A'),
        (WAITING, 'Waiting on Client'),
    )
    status = models.CharField(choices=STATUS_CHOICES, null=True, blank=True,
                              max_length=255)

    def __str__(self):
        return self.name

    def status_color(self):
        """
        Yes                 green
        No                  red
        N/A                 light gray
        Waiting for client  yellow
        """
        mapper = {
            'Yes': 'lightgreen',
            'No': '#ff6666',
            'N/A': '#fcfcfc',
            'Waiting on Client': 'lightyellow'
        }
        if self.status:
            return mapper[self.status.name]
        else:
            return '#fff'

    def log(self):
        return LogEntry.objects.filter(
            content_type_id=ContentType.objects.get_for_model(Assignment).pk,
            object_id=self.pk,
        ).order_by('-action_time').first()

    class Meta:
        db_table = 'assignments'
        ordering = ['order', 'name']

@receiver(post_save, sender=Client)
def gen_default_tasks(sender, instance, created, **kwargs):
    if created:
        for template_assignment in TemplateAssignment.objects.all():
            assignment = Assignment(
                client=instance,
                channel=template_assignment.channel,
                name=template_assignment.name,
                order=template_assignment.order,
            )
            assignment.save()
