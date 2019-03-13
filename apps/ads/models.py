import decimal
from django.db import models
from django_extensions.db.models import TimeStampedModel
from ads.api import adwords
from ads.api import bingads
from ads.api import facebookads
from base import utils
from clients.models import Client


class Ad(TimeStampedModel):
    """Ads Data Report"""
    client = models.ForeignKey('clients.Client', related_name='ads', null=True)
    conversions_adwords = models.DecimalField(
        'Conversions (Adwords)', max_digits=16, decimal_places=0, null=True)
    cost_adwords = models.DecimalField(
        'Cost (AdWords)', max_digits=16, decimal_places=2, null=True)
    conversions_bingads = models.DecimalField(
        'Conversions (BingAds)', max_digits=16, decimal_places=0, null=True)
    cost_bingads = models.DecimalField(
        'Cost (BingAds)', max_digits=16, decimal_places=2, null=True)
    conversions_facebookads = models.DecimalField(
        'Conversions (FacebookAds)', max_digits=16, decimal_places=0,
        null=True)
    cost_facebookads = models.DecimalField(
        'Cost (FacebookAds)', max_digits=16, decimal_places=2, null=True)

    # TODO use a special structure instead of dictionary here. Consider this

    @property
    def facebookads(self):
        return {
            'conversions': self.conversions_facebookads,
            'planned_conversions': self.client.planned_conversions_facebookads,
            'planned_cpa': self.client.planned_cpa_facebookads,
            'spend': self.cost_facebookads,
            'budget': self.client.planned_budget_facebookads
        }

    @property
    def bingads(self):
        return {
            'conversions': self.conversions_bingads,
            'planned_conversions': self.client.planned_conversions_bingads,
            'planned_cpa': self.client.planned_cpa_bingads,
            'spend': self.cost_bingads,
            'budget': self.client.planned_budget_bingads
        }

    @property
    def adwords(self):
        return {
            'conversions': self.conversions_adwords,
            'planned_conversions': self.client.planned_conversions_adwords,
            'planned_cpa': self.client.planned_cpa_adwords,
            'spend': self.cost_adwords,
            'budget': self.client.planned_budget_adwords,
        }

    def sync_adwords(self):
        if self.client.adwords_id:
            try:
                api = adwords.API()
                customer_id = utils.unique_id_serialize(self.client.adwords_id)
                data = api.get_report(api.account_performance_report(),
                                      customer_id, adwords.Serializer)

                if data:
                    self.conversions_adwords = data['Conversions']
                    self.cost_adwords = data['Cost']
                    self.save()
                    print(self.client)
            except:
                self.client.failed_tries += 1
                self.client.save()

    def sync_bingads(self):
        # TODO Do it once in an hour as init extacts all the data at the moment
        if self.client.bingads_id:
            api = bingads.API()
            for item in api.as_dataset().dict:
                if item['AccountId'] == self.client.bingads_id:
                    self.conversions_bingads = int(item['Conversions'])
                    self.cost_bingads = decimal.Decimal(item['Spend'])
                    self.save()

    def sync_facebookads(self):
        if self.client.facebookads_id:
            api = facebookads.API(self.client.facebookads_id)
            if api.data:
                self.conversions_facebookads = api.data[
                    'cost_per_total_action']
                self.cost_facebookads = api.data['spend']
                self.save()

    @staticmethod
    def sync():
        """Sync all enabled clients"""
        clients = Client.objects.filter(is_enabled=True)
        for client in clients:
            if not client.is_custom:
                ad = Ad(client=client)
                ad.sync_adwords()
                ad.sync_bingads()
                ad.sync_facebookads()

    class Meta:
        ordering = ['-created']
