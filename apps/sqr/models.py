import datetime
import logging
from django.db import models
from django.utils import timezone
from django.db.models import (Sum, Case, When, Value, F, ExpressionWrapper,
                              FloatField, IntegerField, DecimalField)
from django_extensions.db.models import TimeStampedModel
# from cities.models import Country
from base.utils import chunks
from ads.api import adwords
from clients.models import Client

logger = logging.getLogger(__name__)


class Report(TimeStampedModel):
    """Record from Search Query Performance Report"""
    client = models.ForeignKey('clients.Client',
                               related_name='sqr_reports', null=True,
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
    term = models.CharField('Search Term', blank=True, null=True,
                            max_length=255, db_index=True)
    author = models.ForeignKey('auth.User', null=True, blank=True,
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
                              blank=True, null=True, default=ACTIVE,
                              db_index=True)

    ADWORDS = 'adwords'
    BINGADS = 'bingads'
    CSV = 'csv'
    SOURCE_CHOICES = (
        (ADWORDS, 'AdWords'),
        (BINGADS, 'BingAds'),
        (CSV, 'csv import'),
    )
    source = models.CharField('Source', choices=SOURCE_CHOICES,
                              default=ADWORDS, max_length=255, null=True,
                              db_index=True)

    DAY1 = '1days'
    DAYS7 = '7days'
    DAYS14 = '14days'
    DAYS30 = '30days'
    DAYS60 = '60days'
    ALLTIME = 'alltime'
    INTERVAL_CHOICES = (
        (DAY1, '1 Day'),
        (DAYS7, '7 Days'),
        (DAYS14, '14 Days'),
        (DAYS30, '30 Days'),
        (DAYS60, '60 Days'),
        (ALLTIME, 'All Time'),
    )
    interval = models.CharField('Interval', choices=INTERVAL_CHOICES,
                                default=ALLTIME, null=True, max_length=50,
                                db_index=True)

    is_countries = models.BooleanField(default=False, db_index=True)
    is_states = models.BooleanField(default=False, db_index=True)
    is_cities = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.term

    @property
    def index(self):
        return None

    @staticmethod
    def sync():
        dfmt = '%Y%m%d'
        clients = Client.objects.filter(is_enabled=True)
        mindate = (timezone.now() - datetime.timedelta(days=60)).strftime(dfmt)
        maxdate = timezone.now().strftime(dfmt)
        for client in clients:
            if not client.is_custom:
                # All Time
                # TODO review if we really can omit delete of ALLTIME data
                # Report.objects\
                #       .filter(client=client, interval=Report.ALLTIME)\
                #       .exclude(status__in=[Report.ADDED, Report.EXCLUDED])\
                #       .delete()
                Report.sync_adwords(client, date_range='ALL_TIME',
                                    interval=Report.ALLTIME)
                # 60 Days
                Report.objects.filter(client=client,
                                      interval=Report.DAYS60).delete()
                Report.sync_adwords(client, min_date=mindate, max_date=maxdate,
                                    interval=Report.DAYS60)
                # 30 Days
                Report.objects.filter(client=client,
                                      interval=Report.DAYS30).delete()
                Report.sync_adwords(client, date_range='LAST_30_DAYS',
                                    interval=Report.DAYS30)
                # 14 Days
                Report.objects.filter(client=client,
                                      interval=Report.DAYS14).delete()
                Report.sync_adwords(client, date_range='LAST_14_DAYS',
                                    interval=Report.DAYS14)
                # 7 Days
                Report.objects.filter(client=client,
                                      interval=Report.DAYS7).delete()
                Report.sync_adwords(client, date_range='LAST_7_DAYS',
                                    interval=Report.DAYS7)
                # 1 Days
                Report.objects.filter(client=client,
                                      interval=Report.DAY1).delete()
                Report.sync_adwords(client, date_range='TODAY',
                                    interval=Report.DAY1)

            Report.sync_bingads(client)

    @staticmethod
    def sync_adwords(client, date_range='YESTERDAY', interval=ALLTIME,
                     min_date=None, max_date=None):
        report = Report(client=client)
        api = adwords.API()
        data = api.get_report(
            api.search_query_performance_report(
                date_range, min_date, max_date),
            client.customer_id, adwords.SQRSerializer)
        if data:
            logger.info(data)
            for item in data:
                if item[0] != 'Total':
                    report = Report.objects.filter(client=client, term=item[4],
                                                   interval=interval).first()
                    if report:
                        report.conversions = item[0]
                        report.cost = item[1]
                        report.impressions = item[2]
                        report.clicks = item[3]
                    else:
                        report = Report(
                            client=client,
                            conversions=item[0],
                            cost=item[1],
                            impressions=item[2],
                            clicks=item[3],
                            term=item[4],
                            interval=interval
                        )
                    report.save()

            # for reports_part in chunks(reports, 100):
            #     Report.objects.bulk_create(reports_part)
        else:
            logger.warning(f'No SQR data for {client}')

    @staticmethod
    def sync_bingads(client):
        # TODO
        # report = Report(client=client, source=Report.BINGADS)
        # report.save()
        pass

    @staticmethod
    def sync_csv(client):
        """TODO"""
        report = Report(client=client, source=Report.CSV)
        report.save()

    @staticmethod
    def data_total():
        qs = Report.objects.filter(interval=Report.ALLTIME).aggregate(
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
    def sqr_annotate(cls, client_id=None, qs=None, status=None,
                     interval=ALLTIME):
        if client_id:
            client = Client.objects.get(pk=client_id)
            qs = client.sqr_reports
        dt = cls.data_total()
        if status:
            qs = qs.filter(status=status)
        raw = qs.filter(interval=interval).annotate(
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
        qs = qs.filter(interval=Report.ALLTIME).aggregate(
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
        ordering = ['term']
        db_table = 'sqr_reports'
