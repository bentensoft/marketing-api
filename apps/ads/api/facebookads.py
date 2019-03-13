import calendar
from django.utils import timezone
from django.conf import settings
from facebookads.adobjects.adaccount import AdAccount
from facebookads.api import FacebookAdsApi
from preferences.models import Preferences


class API(object):

    def __init__(self, account_id):
        prefs = Preferences.objects.get()
        ad_account_id = 'act_%s' % account_id
        FacebookAdsApi.init(access_token=prefs.facebook_access_token)
        fields = [
            'account_id',
            'account_name',
            'cost_per_total_action',
            'impressions',
            'total_action_value',
            'spend',
        ]
        now = timezone.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        params = {
            'time_range': {'since': now.strftime('%Y-%m-01'),
                           'until': now.strftime('%Y-%m-') + '%s' % last_day},
            'filtering': [],
            'level': 'account',
            'breakdowns': [],
        }
        try:
            self.data = AdAccount(ad_account_id).get_insights(fields=fields,
                                                              params=params)[0]
        except:
            self.data = None
