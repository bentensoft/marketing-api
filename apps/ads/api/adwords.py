import decimal
import tablib
from googleads.adwords import AdWordsClient
from googleads.oauth2 import GoogleRefreshTokenClient
from django.conf import settings
from preferences.models import Preferences




def dec(value):
    return decimal.Decimal(value)


class Serializer(object):
    """AdWords serializer"""

    def __init__(self, stream, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
        self.stream = stream

    def to_python(self):
        """Must be universal for report structure"""
        data = self.stream.decode('utf-8').split('\n')
        headers = data[1].split(',')
        values = data[2].split(',')
        data = dict(zip(headers, values))

        if data.get('Conversions'):
            try:
                data['Conversions'] = float(data['Conversions'])
            except:
                data['Conversions'] = 0.0

        if data.get('Cost'):
            try:
                data['Cost'] = dec(data['Cost']) / dec(1000000)
            except:
                data['Cost'] = dec('0.0')

        return data


class SQRSerializer(object):
    """AdWords serializer"""

    def __init__(self, stream, *args, **kwargs):
        super(SQRSerializer, self).__init__(*args, **kwargs)
        self.stream = stream

    def to_python(self):
        """Must be universal for report structure"""
        raw = self.stream.decode('utf-8').split('\n')
        data = tablib.Dataset()
        data.headers = raw[1].split(',')

        for raw_row in raw[2:-1]:
            row = raw_row.split(',')
            row[1] = dec(row[1]) / dec(1000000)
            data.append(row)

        return data


class PPRSerializer(object):
    """AdWords serializer"""

    def __init__(self, stream, *args, **kwargs):
        super(PPRSerializer, self).__init__(*args, **kwargs)
        self.stream = stream

    def to_python(self):
        """Must be universal for report structure"""
        raw = self.stream.decode('utf-8').split('\n')
        data = tablib.Dataset()
        data.headers = raw[1].split(',')

        for raw_row in raw[2:-1]:
            row = raw_row.split(',')
            row[1] = dec(row[1]) / dec(1000000)
            try:
                data.append(row)
            except:
                # TODO notify sentry about error details
                pass

        return data


class API(object):

    VERSION = 'v201708'
    DECIMAL_STEP = 1000000

    def __init__(self, *args, **kwargs):
        prefs = Preferences.objects.get()
        credentials = GoogleRefreshTokenClient(prefs.adwords_client_id,
                                               prefs.adwords_client_secret,
                                               prefs.adwords_refresh_token)
        self._USER_AGENT = 'Yael Consulting Web'
        self.client = AdWordsClient(
            prefs.adwords_dev_token, credentials,
            self._USER_AGENT,
            client_customer_id=prefs.adwords_manager_id)

    def get_customer_ids(self):
        """Get customer IDs"""
        managed_customer_service = self.client.GetService(
            'ManagedCustomerService', version=self.VERSION)
        selector = {
            'fields': ['CustomerId'],
            'predicates': [{
                'field': 'CanManageClients',
                'operator': 'EQUALS',
                'values': [False]
            }],
        }
        page = managed_customer_service.get(selector)
        return [customer['customerId'] for customer in page.entries]

    def search_query_performance_report(self, date_range='YESTERDAY',
                                        min_date=None, max_date=None):
        """Contains conversion, costs
        https://developers.google.com/adwords/api/docs/appendix/reports/search-query-performance-report
        Date Range: https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges
        min_date or max_date format is YYYYMMDD according to the docs
        """
        # TODO make assert on possible values here
        data = {
            'reportName': 'Search Query Performance Report',
            'dateRangeType': date_range,
            'reportType': 'SEARCH_QUERY_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['Conversions', 'Cost', 'Impressions', 'Clicks',
                           'Query'],
            }
        }
        if min_date and max_date:
            data['dateRangeType'] = 'CUSTOM_DATE'
            data['selector']['dateRange'] = {
                'min': min_date,
                'max': max_date
            }
        return data


    def keywords_performance_report(self, date_range='YESTERDAY',
                                          min_date=None, max_date=None):
        """Contains conversion, costs
        https://developers.google.com/adwords/api/docs/appendix/reports/search-query-performance-report
        Date Range: https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges
        min_date or max_date format is YYYYMMDD according to the docs
        """
        # TODO make assert on possible values here
        data = {
            'reportName': 'Keywords Query Performance Report',
            'dateRangeType': date_range,
            'reportType': 'KEYWORDS_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['Conversions', 'Cost', 'Impressions', 'Clicks',
                           ],
            }
        }
        if min_date and max_date:
            data['dateRangeType'] = 'CUSTOM_DATE'
            data['selector']['dateRange'] = {
                'min': min_date,
                'max': max_date
            }
        return data

    def placement_performance_report(self, date_range='ALL_TIME'):
        """Contains conversion, costs
        https://developers.google.com/adwords/api/docs/appendix/reports/account-performance-report
        Date Range: https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges
        min_date or max_date format is YYYYMMDD according to the docs
        """
        # TODO make assert on possible values here
        data = {
            'reportName': 'Placements Performance Report',
            'dateRangeType': date_range,
            'reportType': 'PLACEMENT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['Conversions', 'Cost', 'Impressions', 'Clicks', 'DisplayName'],
            }
        }
        return data

    def account_performance_report(self, date_range='THIS_MONTH',
                                   min_date=None, max_date=None):
        """Contains conversion, costs
        https://developers.google.com/adwords/api/docs/appendix/reports/account-performance-report
        min_date or max_date format is YYYYMMDD according to the docs
        """
        # TODO make assert on possible values here
        data = {
            'reportName': 'Account Performance Report',
            'dateRangeType': date_range,
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['Conversions', 'Cost', 'Impressions', 'Clicks'],
            }
        }
        if min_date and max_date:
            data['dateRangeType'] = 'CUSTOM_DATE'
            data['selector']['dateRange'] = {
                'min': min_date,
                'max': max_date
            }
        return data

    def get_report(self, definition, customer_id, serializer=Serializer):
        """Get report by definition for the customer by his ID"""
        report_downloader = self.client.GetReportDownloader(
            version=self.VERSION)
        try:
            report = report_downloader.DownloadReportAsStream(
                definition, client_customer_id=customer_id)
        # Check for exactly googleads.errors.AdWordsReportBadRequestError:
        # Type: AuthenticationError.CUSTOMER_NOT_FOUND
        except:
            return None

        return serializer(report.read()).to_python()
