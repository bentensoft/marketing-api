from django.db import models
from django_extensions.db.models import TimeStampedModel
from rest_framework.exceptions import ValidationError

from .managers import SyncManager


def validate_google_spreadsheet_link(value):
    if not value.startswith("https://docs.google.com/spreadsheets/"):
        raise ValidationError(
            '%s is not a valid google spreadsheet link' % value,
            code=400,
        )


class Client(TimeStampedModel):
    """Client is stored here. Client can be managed by several users"""

    name = models.CharField('Name', max_length=255, null=True, blank=False)
    logo = models.ImageField(upload_to='client_logos/', null=True, blank=True)
    adwords_id = models.CharField('AdWords ID', max_length=255, null=True,
                                  blank=True, unique=True)
    bingads_id = models.CharField('BingAds ID', max_length=255, null=True,
                                  blank=True, unique=True)
    facebookads_id = models.CharField('Facebook Ads ID', max_length=255,
                                      null=True, blank=True, unique=True)

    is_enabled = models.BooleanField(default=False, blank=True)
    is_custom = models.BooleanField(default=False)
    master = models.ForeignKey('Client', verbose_name='Master',
                               blank=True, null=True, related_name='clients')
    failed_tries = models.PositiveIntegerField(
        default=0, null=True, blank=True, help_text='used to notify on fails')

    # Planned
    planned_budget_adwords = models.DecimalField(
        'Goal for Spend (AdWords)', max_digits=16, decimal_places=2, null=True,
        blank=True)
    planned_cpa_adwords = models.DecimalField(
        'Goal for CPA (AdWords)', max_digits=16, decimal_places=2, null=True,
        blank=True)
    planned_conversions_adwords = models.DecimalField(
        'Goal for Conversion (AdWords)', max_digits=16, decimal_places=2,
        null=True, blank=True)

    planned_budget_bingads = models.DecimalField(
        'Goal for Spend (BingAds)', max_digits=16, decimal_places=2, null=True,
        blank=True)
    planned_cpa_bingads = models.DecimalField(
        'Goal for CPA (BingAds)', max_digits=16, decimal_places=2, null=True,
        blank=True)
    planned_conversions_bingads = models.DecimalField(
        'Goal for Conversion (BingAds)', max_digits=16, decimal_places=2,
        null=True, blank=True)

    planned_budget_facebookads = models.DecimalField(
        'Goal for Spend (FacebookAds)', max_digits=16, decimal_places=2,
        null=True, blank=True)
    planned_cpa_facebookads = models.DecimalField(
        'Goal for CPA (FacebookAds)', max_digits=16, decimal_places=2,
        null=True, blank=True)
    planned_conversions_facebookads = models.DecimalField(
        'Goal for Conversion (FacebookAds)', max_digits=16, decimal_places=2,
        null=True, blank=True)

    google_spreadsheet = models.URLField(
        'Google spreadsheet SQR', blank=True, null=True,
        validators=[validate_google_spreadsheet_link])

    sync = SyncManager()

    def __str__(self):
        return self.name or 'Undefined'

    @property
    def customer_id(self):
        """Customer ID at Google AdWords"""
        return self.adwords_id.replace('-', '')

    def onboarding_percent_completed(self):
        # TODO replace n/a and yes with constant values like YES or NA
        # completed = self.assignments.exclude(status='n/a')\
        #                             .filter(status='yes')\
        #                             .count()
        completed = 0

        # overall = self.assignments.exclude(status='n/a').count()
        overall = 0
        if overall:
            return completed * 100 / overall
        return 0

    class Meta:
        ordering = ['name']
