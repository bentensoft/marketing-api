from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.db.models.aggregates import Sum


class Ngram(TimeStampedModel):
    """n-gram data structure to store words and its data"""
    client = models.ForeignKey('clients.Client', blank=False, null=True,
                               on_delete=models.CASCADE, related_name='ngrams')
    word = models.CharField('Word', max_length=255, blank=False, null=True)
    impressions = models.DecimalField('Impressions', max_digits=18,
                                      decimal_places=6, null=True,
                                      db_index=True)
    clicks = models.DecimalField('Clicks', max_digits=18, decimal_places=6,
                                 null=True, db_index=True)
    cost = models.DecimalField('Cost',
                               max_digits=18, decimal_places=6,
                               null=True, db_index=True)
    conversions = models.DecimalField('Conversions', max_digits=18,
                                      decimal_places=6, null=True,
                                      db_index=True)

    ADDED = 'added'
    EXCLUDED = 'excluded'
    ACTIVE = 'active'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (ADDED, 'Added'),
        (EXCLUDED, 'Excluded')
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              blank=True, null=True, default=ACTIVE)

    @staticmethod
    def data_total(client):
        qs = Ngram.objects.filter(client=client).aggregate(
            Sum('impressions'),
            Sum('cost'),
            Sum('clicks'),
            Sum('conversions')
        )
        if qs.get('impressions__sum') and qs.get('conversions__sum'):
            qs.update({
                'ctr': qs['clicks__sum'] * 100 / qs['impressions__sum'],
                'cpa': qs['cost__sum'] / qs['conversions__sum']
            })
        else:
            qs.update({
                'ctr': None,
                'cpa': None
            })
        return qs

    def __str__(self):
        return self.word
