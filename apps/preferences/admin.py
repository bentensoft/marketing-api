from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Preferences


@admin.register(Preferences)
class PreferencesAdmin(SingletonModelAdmin):
    fieldsets = (
        ('AdWords', {
            'fields': [
                'adwords_dev_token',
                'adwords_client_id',
                'adwords_client_secret',
                'adwords_refresh_token',
                'adwords_manager_id'
            ]
        }),
        ('BingAds', {
            'fields': [
                'bing_access_token',
                'bing_refresh_token',
                'bing_expires_in',
                'bing_client_id',
                'bing_client_secret',
                'bing_account_id',
                'bing_customer_id',
                'bing_dev_token',
                'bing_mode',
            ]
        }),
        ('FacebookAds', {
            'fields': [
                'facebook_app_id',
                'facebook_app_secret',
                'facebook_app_token',
                'facebook_access_token'
            ]
        }),
    )
