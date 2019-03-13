from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from solo.models import SingletonModel


class Preferences(SingletonModel):
    bing_access_token = models.TextField(blank=True, null=True)
    bing_refresh_token = models.TextField(blank=True, null=True)
    bing_expires_in = models.DateTimeField(blank=True, null=True)

    facebook_app_id = models.TextField(_('Facebook App ID'), blank=True,
                                       null=True) 
    facebook_app_secret = models.TextField(_('Facebook App Secret'),
                                           blank=True, null=True)
    facebook_app_token = models.TextField(_('Facebook App Token'), blank=True,
                                          null=True)
    facebook_access_token = models.TextField(_('Facebook Access Token'),
                                             blank=True, null=True)

    bing_client_id = models.TextField(_('Bing Client ID'), blank=True,
                                      null=True)
    bing_client_secret = models.TextField(_('Bing Client Secret'), blank=True,
                                          null=True)
    bing_account_id = models.TextField(_('Bing Account ID'), blank=True,
                                       null=True)
    bing_customer_id = models.TextField(_('Bing Customer ID'), blank=True,
                                        null=True)
    bing_dev_token = models.TextField(_('Bing Dev Token'), blank=True,
                                      null=True)
    bing_mode = models.TextField(_('Bing mode'), blank=True, null=True)

    adwords_dev_token = models.CharField(_('AdWords Dev Token'), blank=True,
                                         null=True, max_length=255)
    adwords_client_id = models.CharField(_('AdWords Client ID'), blank=True,
                                         null=True, max_length=255)
    adwords_client_secret = models.TextField(_('AdWords Client Secret'),
                                             blank=True, null=True)
    adwords_refresh_token = models.TextField(_('AdWords Refresh Token'),
                                             blank=True, null=True)
    adwords_manager_id = models.CharField(_('AdWords Manager ID'), blank=True,
                                          null=True, max_length=255)


    def __str__(self):
        return 'Preferences'

    class Meta:
        verbose_name = "Preferences"
        db_table = 'preferences'
