import os
import tablib
import logging
import datetime
from django.utils import timezone
from django.conf import settings
from bingads.authorization import OAuthWebAuthCodeGrant
from preferences.models import Preferences
from bingads.authorization import AuthorizationData
from bingads.v11.reporting import ReportingServiceManager
from bingads.v11.reporting import ServiceClient
from bingads.v11.reporting import ReportingDownloadParameters
from bingads.authorization import OAuthTokens
from preferences.models import Preferences


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)



class API(object):
    """Bing API implementation over poor bingads to simplify interaction"""
    def __init__(self):
        self.auth_data = OAuthWebAuthCodeGrant(
            client_id=prefs.bing_client_id,
            client_secret=prefs.bing_client_secret,
            redirection_uri='https://app.yaelconsulting.com/bing/',
        )
        prefs = Preferences.objects.get()
        self.ENVIRONMENT = prefs.bing_mode 
        self.FILE_DIRECTORY = os.getcwd()
        self.DOWNLOAD_FILE_NAME = 'bingads.csv'
        self.REPORT_FILE_FORMAT = 'Csv'
        self.TIMEOUT_IN_MILLISECONDS = 3600000
        # TODO implement csrf protection
        # auth_data.state = ""

        mtime = os.path.getmtime(self.DOWNLOAD_FILE_NAME)
        modified = datetime.datetime.fromtimestamp(mtime)
        now = datetime.datetime.now()

        # if exceeds 1 hour then update
        # if (now - modified).seconds / 60 > 60:
            # auth_data._oauth_tokens = self.get_oauth_tokens()
        auth_data = OAuthWebAuthCodeGrant(
            client_id=prefs.bing_client_id,
            client_secret=prefs.bing_client_secret,
            redirection_uri='https://app.yaelconsulting.com/bing/',
            oauth_tokens=self.get_oauth_tokens()
        )

        self.authorization_data = AuthorizationData(
            authentication=auth_data,
            customer_id=prefs.bing_customer_id,
            account_id=prefs.bing_account_id,
            developer_token=prefs.bing_dev_token
        )

        self.service_manager = ReportingServiceManager(
            self.authorization_data,
            poll_interval_in_milliseconds=5000,
            environment=self.ENVIRONMENT)

        self.service_client = ServiceClient(
            'ReportingService',
            authorization_data=self.authorization_data,
            environment=self.ENVIRONMENT,
            version=11)


    def get_report(self, report_request):

        reporting_download_parameters = ReportingDownloadParameters(
            report_request=report_request,
            result_file_directory=self.FILE_DIRECTORY,
            result_file_name=self.DOWNLOAD_FILE_NAME,
            overwrite_result_file=True,
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS
        )
        logger.info(
            report_request, self.FILE_DIRECTORY, self.DOWNLOAD_FILE_NAME,
            self.TIMEOUT_IN_MILLISECONDS)

        try:
            self.service_manager.download_file(reporting_download_parameters)
        except Exception as e:
            logger.error(e)

    def get_oauth_tokens(self):
        prefs = Preferences.objects.get()
        return OAuthTokens(access_token=prefs.bing_access_token,
                           access_token_expires_in_seconds=3600,
                           refresh_token=prefs.bing_refresh_token)

    def get_account_performance_report(self):
        report_request = self.service_client.factory\
                             .create('AccountPerformanceReportRequest')
        report_request.Format = self.REPORT_FILE_FORMAT
        report_request.ReportName = 'Yael App Report'
        report_request.ReturnOnlyCompleteData = False
        report_request.Aggregation = 'Daily'
        report_request.Language = 'English'

        today = datetime.date.today()
        report_time = self.service_client.factory.create('ReportTime')
        # report_time.PredefinedTime = 'ThisMonth'
        custom_date_range_start = self.service_client.factory.create('Date')
        custom_date_range_start.Day = 1
        custom_date_range_start.Month = today.month
        custom_date_range_start.Year = today.year
        report_time.CustomDateRangeStart = custom_date_range_start
        custom_date_range_end = self.service_client.factory.create('Date')
        custom_date_range_end.Day = today.day
        custom_date_range_end.Month = today.month
        custom_date_range_end.Year = today.year
        report_time.CustomDateRangeEnd = custom_date_range_end
        report_time.PredefinedTime = None
        report_request.Time = report_time

        # report_columns = self.service_client.factory\
        #                      .create('AccountPerformanceReportColumn')
        report_request.Columns.AccountPerformanceReportColumn.append([
            'AccountId',
            'Clicks',
            'Spend',
            'Conversions'
        ])

        return report_request

    def get_search_performance_report(self):
        report_request = self.service_client.factory\
                             .create('SearchQueryPerformanceReportRequest')
        report_request.Format = self.REPORT_FILE_FORMAT
        report_request.ReportName = 'Yael App Report'
        report_request.ReturnOnlyCompleteData = False
        report_request.Aggregation = 'Daily'
        report_request.Language = 'English'

        today = datetime.date.today()
        report_time = self.service_client.factory.create('ReportTime')
        # report_time.PredefinedTime = 'ThisMonth'
        custom_date_range_start = self.service_client.factory.create('Date')
        custom_date_range_start.Day = 1
        custom_date_range_start.Month = today.month
        custom_date_range_start.Year = today.year
        report_time.CustomDateRangeStart = custom_date_range_start
        custom_date_range_end = self.service_client.factory.create('Date')
        custom_date_range_end.Day = today.day
        custom_date_range_end.Month = today.month
        custom_date_range_end.Year = today.year
        report_time.CustomDateRangeEnd = custom_date_range_end
        report_time.PredefinedTime = None
        report_request.Time = report_time

        # report_columns = self.service_client.factory\
        #                      .create('AccountPerformanceReportColumn')
        report_request.Columns.AccountPerformanceReportColumn.append([
            'Clicks',
            'Spend',
            'Conversions',
            'Impressions',
            'SearchQuery'
        ])

        return report_request

    def as_dataset(self):
        bingads_csv = open('bingads.csv').read()
        raw = bingads_csv.split('\n')
        rows = raw[10:-3]
        return tablib.Dataset().load('\n'.join(rows))

    def refresh_tokens(self):
        prefs = Preferences.objects.get()
        token = prefs.bing_refresh_token
        try:
            oauth_tokens = self.auth_data.request_oauth_tokens_by_refresh_token(token)
            prefs.bing_access_token = oauth_tokens.access_token
            prefs.bing_refresh_token = oauth_tokens.refresh_token
            prefs.bing_expires_in = timezone.now() + datetime.timezone(
                seconds=oauth_tokens.access_token_expires_in_seconds)
            from .tasks import refresh_tokens
            eta = prefs.bing_expires_in - datetime.timedelta(minutes=5)
            refresh_tokens.apply_async(eta=eta)
        except:
            pass
            # prefs.bing_access_token = None
            # prefs.bing_refresh_token = None
            # prefs.bing_expires_in = None

        prefs.save()
