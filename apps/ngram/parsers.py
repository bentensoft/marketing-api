import logging
from django.db.models import Sum
from sqr.models import Report
from .models import Ngram


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NgramParser(object):

    def __init__(self, client):
        self.client = client
        self.words = self.get_words(client)

    def get_words(self, client):
        avoid_terms = client.sqr_reports\
                            .filter(status=Report.EXCLUDED)\
                            .values_list('term', flat=True)
        whole = ''.join(client.sqr_reports.exclude(term__in=avoid_terms)
                              .values_list('term', flat=True))
        words = set(whole.split(' '))
        # remove those ones
        EXCLUDE = ['and', 'or', 'the', 'a', 'an', 'by', 'in']
        for word in EXCLUDE:
            try:
                words.remove(word)
            except KeyError:
                pass

        return words

    def data(self, word):
        # TODO make custom manager like client.sqr.active
        reports = self.client.sqr_reports.filter(status=Report.ACTIVE)
        qs = reports.filter(term__icontains=word).aggregate(
            Sum('impressions'),
            Sum('cost'),
            Sum('clicks'),
            Sum('conversions')
        )
        if qs.get('impressions__sum') != 0 and qs.get('conversions__sum') != 0:
            try:
                qs.update({
                    'ctr': qs['clicks__sum'] * 100 / qs['impressions__sum'],
                    'cpa': qs['cost__sum'] / qs['conversions__sum'],
                    'cpc': qs['cost__sum'] / qs['clicks__sum']
                })
            except:
                qs.update({
                    'ctr': None,
                    'cpa': None,
                    'cpc': None
                })
        else:
            qs.update({
                'ctr': None,
                'cpa': None,
                'cpc': None
            })
        return qs

    def process(self):
        logger.info('NGRAM generation for %s' % self.client)
        self.client.ngrams.all().delete()
        total = len(self.words)
        for i, word in enumerate(self.words):
            data = self.data(word)
            if any([
                data['impressions__sum'],
                data['clicks__sum'],
                data['cost__sum'],
                data['conversions__sum']
            ]) and len(word) > 1:
                item = Ngram(client=self.client, word=word)
                item.impressions = data['impressions__sum']
                item.clicks = data['clicks__sum']
                item.cost = data['cost__sum']
                item.conversions = data['conversions__sum']
                item.save()
            logger.info('[%s from %s]\t\t[%s]' % (i, total, word))
        logger.info('NGRAM generation completed')
