import decimal
import logging
from django.db import models
from django.db.models import (Sum, Case, When, ExpressionWrapper, Value, F,
                              IntegerField, FloatField, DecimalField)
from django_extensions.db.models import TimeStampedModel
from ads.api import adwords
from clients.models import Client


logger = logging.getLogger(__name__)


class PPR(TimeStampedModel):
    """Record from Search Query Performance Report"""
    client = models.ForeignKey('clients.Client',
                               related_name='pprs', null=True,
                               db_index=True)
    impressions = models.DecimalField('Impressions',
                                      max_digits=18, decimal_places=6,
                                      null=True, db_index=True)
    clicks = models.DecimalField('Clicks',
                                 max_digits=18, decimal_places=6,
                                 null=True, db_index=True)
    cost = models.DecimalField('Cost',
                               max_digits=18, decimal_places=6,
                               null=True, db_index=True)
    conversions = models.DecimalField('Conversions',
                                      max_digits=18, decimal_places=6,
                                      null=True, db_index=True)
    placement = models.CharField('Search Term', blank=True, null=True,
                                 max_length=255, db_index=True)
    author = models.ForeignKey('auth.User', null=True, blank=True)

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

    ADWORDS = 'adwords'
    BINGADS = 'bingads'
    CSV = 'csv'
    SOURCE_CHOICES = (
        (ADWORDS, 'AdWords'),
        (BINGADS, 'BingAds'),
        (CSV, 'csv import'),
    )
    source = models.CharField('Source', choices=SOURCE_CHOICES,
                              default=ADWORDS, max_length=255, null=True)

    def __str__(self):
        return self.placement

    @property
    def index(self):
        return None

    @staticmethod
    def sync():
        clients = Client.objects.filter(is_enabled=True, is_custom=False)
        for client in clients:
            PPR.sync_adwords(client)
            PPR.sync_bingads(client)

    @staticmethod
    def sync_adwords(client):
        PPR.objects.filter(client=client, status=PPR.ACTIVE).delete()
        ppr = PPR(client=client)
        api = adwords.API()
        data = api.get_report(api.placement_performance_report(),
                              client.customer_id, adwords.PPRSerializer)
        if data:
            logger.info(data)
            for item in data:
                if item[0] != 'Total':
                    qs = PPR.objects.filter(client=client)
                    ppr = qs.filter(placement=item[4]).first()
                    if ppr:
                        ppr.conversions += decimal.Decimal(item[0])
                        ppr.cost += decimal.Decimal(item[1])
                        ppr.impressions += decimal.Decimal(item[2])
                        ppr.clicks += decimal.Decimal(item[3])
                    else:
                        ppr = PPR(
                            client=client,
                            conversions=decimal.Decimal(item[0]),
                            cost=item[1],
                            impressions=item[2],
                            clicks=item[3],
                            placement=item[4],
                        )
                    ppr.save()
        else:
            logger.warning(f'PPR data is empty {client}')

    @staticmethod
    def sync_bingads(client):
        # TODO
        # report = Report(client=client, source=Report.BINGADS)
        # report.save()
        pass

    @staticmethod
    def sync_csv(client):
        """TODO"""
        ppr = PPR(client=client, source=Report.CSV)
        ppr.save()

    @staticmethod
    def data_total():
        qs = PPR.objects.aggregate(
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

    @classmethod
    def ppr_annotate(cls, client_id=None, qs=None, status=None):
        if not any([client_id, qs]):
            return qs
        if client_id:
            client = Client.objects.get(pk=client_id)
            qs = client.pprs
        dt = cls.data_total()
        if status:
            qs = qs.filter(status=status)
        raw = qs.annotate(
            Sum('impressions'),
            Sum('cost'),
            Sum('clicks'),
            Sum('conversions'),
            cpc=Case(
                When(clicks__sum=0, then=Value(0)),
                default=ExpressionWrapper(F('cost__sum') / F('clicks__sum'), IntegerField()),
                output_field=FloatField()
            ),
            ctr=Case(
                When(impressions__sum=0, then=Value(0)),
                default=ExpressionWrapper(F('clicks__sum') * 100 / F('impressions__sum'), IntegerField()),
                output_field=FloatField()
            ),
            cpa=Case(
                When(conversions__sum=0, then=Value(0)),
                default=ExpressionWrapper(F('cost__sum') / F('conversions__sum'), IntegerField()),
                output_field=FloatField()
            ),
            i=ExpressionWrapper(
                (F('impressions__sum') / dt['clicks__sum']) if dt['clicks__sum'] else 0 +
                (F('clicks__sum') / dt['ctr']) if dt['ctr'] else 0 +
                (F('cost__sum') / dt['conversions__sum']) if dt['conversions__sum'] else 0 +
                (F('conversions__sum') / dt['cpa']) if dt['cpa'] else 0,
                DecimalField(max_digits=24, decimal_places=24)
            )
        )
        return raw

    @staticmethod
    def total(qs):
        qs = qs.aggregate(
            impressions=Sum('impressions'),
            cost=Sum('cost'),
            clicks=Sum('clicks'),
            conversions=Sum('conversions')
        )

        if qs.get('impressions'):
            qs['ctr'] = qs['clicks'] * 100 / qs['impressions']
        else:
            qs['ctr'] = None

        if qs.get('conversions'):
            qs['cpa'] = qs['cost'] / qs['conversions']
        else:
            qs['cpa'] = None

        if qs.get('clicks'):
            qs['cpc'] = qs['cost'] / qs['clicks']
        else:
            qs['cpc'] = None

        qs['index'] = sum([
            (qs['impressions'] / qs['clicks']) if qs['clicks'] else 0,
            (qs['clicks'] / qs['ctr']) if qs['ctr'] else 0,
            (qs['cost'] / qs['conversions']) if qs['conversions'] else 0,
            (qs['conversions'] / qs['cpa']) if qs['cpa'] else 0,
        ])

        return qs

    class Meta:
        ordering = ['placement']
        db_table = 'pprs'
