import codecs
import csv

import chardet
import gspread
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from cities.models import Country

from .models import Report
from . import serializers
from base import mixins
from base.parsers import SearchParser
from ngram.tasks import build_ngram
from oauth2client.service_account import ServiceAccountCredentials
from .tasks import sync
from django.core.cache import cache


# Temp:
class SQRListOld(mixins.AdminPermission, generics.ListAPIView):


    # cpc = cost / click
    #
    serializer_class = serializers.ReportSerializer
    def get_pk(self):
        return int(self.kwargs.get('pk'))

    def get_status(self):
        return self.request.GET.get('status', Report.ACTIVE)

    def get_interval(self):
        return self.request.GET.get('interval', Report.ALLTIME)


    def get_queryset_kwargs(self):
        kwargs = {
            'client_id': self.get_pk(),
            'status': self.get_status(),
        }

        if self.get_interval() != Report.ALLTIME:
            kwargs['interval'] = self.get_interval()

        return kwargs

    def get_queryset(self):
        predefined = Q()
        queryset = Report.objects.filter(predefined)

        return queryset

    def list(self, request, *args, **kwargs):
        context = {
            'request': request,
        }

        if self.request.GET.get('q', '') in [None,'']:

            qs = self.get_queryset()

        else:
            search = SearchParser(Report, self.request.GET.get('q', ''), 'term')


            print('qskw: %s' % str(self.get_queryset_kwargs()))
            qs = search.get_queryset(**self.get_queryset_kwargs())

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context=context)
            response = self.get_paginated_response(serializer.data)
            # search_total = Report.total(qs)
            search_total = {
                "impressions": 5161900.0,
                "cost": 153512.07,
                "clicks": 221702.0,
                "conversions": 6431.0,
                "ctr": 4.294968906797885,
                "cpa": 23.87063753693049,
                "cpc": 0.6924252825865351,
                "index": 51935.56417665853
            }
            response.data.update({'search_total': search_total})
            return response


        qs = self.get_queryset()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class SQRList(mixins.AdminPermission, generics.ListAPIView):
    serializer_class = serializers.ReportSerializer

    def get_pk(self):
        return int(self.kwargs.get('pk'))

    def get_status(self):
        return self.request.GET.get('status', Report.ACTIVE)

    def get_interval(self):
        return self.request.GET.get('interval', Report.ALLTIME)

    def get_queryset_kwargs(self):
        kwargs = {
            'client_id': self.get_pk(),
            'status': self.get_status(),
        }

        if self.get_interval() != Report.ALLTIME:
            kwargs['interval'] = self.get_interval()

        return kwargs

    def get_filters(self):
        raw = self.request.GET.get('filters', None)
        predefined = Q()
        # TODO refactor this if-for-if shit later
        # kwargs = {}
        # if raw:
        #     for item in raw.split(','):
        #         if item == 'countries':
        #             kwargs['is_countries'] = True
        #         elif item == 'usa_states':
        #             kwargs['is_states'] = True
        #         elif item == 'top_usa_cities':
        #             kwargs['is_cities'] = True
        if raw:
            for item in raw.split(','):
                if item == 'country':
                    countries = Country.objects.values_list('name', flat=True)
                    for country in countries:
                        q = Q(term__icontains=country)
                        predefined = (predefined and (predefined | q)) or q
                elif item == 'usa_states':
                    states = Country.objects.get(name='United States')\
                                    .regions.values_list('name', flat=True)
                    for state in states:
                        q = Q(term__icontains=state)
                        predefined = (predefined and (predefined | q)) or q
                elif item == 'top_usa_cities':
                    cities = Country.objects.get(name='United States')\
                                    .cities.order_by('-population')[:400]
                    for city in cities:
                        q = Q(term__icontains=city)
                        predefined = (predefined and (predefined | q)) or q

        return predefined

    def get_order_by(self):
        return self.request.GET.get('sortBy', '-term')

    def get_queryset(self):

        print("Reached SQRList.get_queryset")
        search = SearchParser(Report, self.request.GET.get('q', ''), 'term')
        qs = search.get_queryset(
            values=['id', 'term', 'impressions', 'clicks', 'cost',
                    'conversions', 'modified'],
            **self.get_queryset_kwargs())
        filters = self.get_filters()
        if filters is not None:
            qs = qs.filter(filters)
        qs = Report.sqr_annotate(qs=qs, interval=self.get_interval())

        if qs is not None:
            return qs.order_by(self.get_order_by())
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        print("Queryset: %s" % queryset.query)
        context = {
            'request': request,
        }

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context=context)
            response = self.get_paginated_response(serializer.data)
            search_total = Report.total(queryset)
            response.data.update({'search_total': search_total})
            return response


class SQRDetail(mixins.AdminPermission, generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'sqr_pk'
    queryset = Report.objects.all()
    serializer_class = serializers.ReportSerializer


class SQRUploadCSV(mixins.AdminPermission, APIView):
    def post(self, request, pk=None, *args, **kwargs):
        if not request.FILES:
            return Response({'detail': 'file required'}, status=status.HTTP_400_BAD_REQUEST)

        if not next(iter(request.FILES.keys())).endswith(".csv"):
            return Response({'detail': 'csv file expected'})

        file_obj = next(iter(request.FILES.values()))
        data = csv.DictReader(codecs.iterdecode(file_obj, chardet.detect(file_obj.read())['encoding']))

        reports = []
        for item in data:
            if set(item.keys()) != {'term', 'impressions', 'clicks', 'cost',
                                    'conversions'}:
                return Response(
                    {'detail': 'wrong file format. it should contains "term", "impressions", "clicks", '
                               '"cost", "conversions" columns'}, status=status.HTTP_400_BAD_REQUEST)
            reports.append(Report(client_id=pk, author=request.user, **item))

        if reports:
            Report.objects.filter(client_id=pk).delete()
            Report.objects.bulk_create(reports)
            build_ngram.s(client_id=pk).apply_async()
            return Response(status=status.HTTP_200_OK)

        return Response({'detail': 'file is empty'}, status=status.HTTP_400_BAD_REQUEST)


class SQRLoadFromGoogleSpreadsheet(mixins.AdminPermission, APIView):
    def post(self, request, pk=None, *args, **kwargs):
        from clients.models import Client
        client = get_object_or_404(Client.objects.all(), pk=pk)
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_CREDENTIALS_JSON, scope)
        gc = gspread.authorize(credentials)
        doc = gc.open_by_url(client.google_spreadsheet)
        wks = doc.sheet1
        parsed_data = wks.get_all_values()
        data = []
        data_keys = parsed_data[0]
        for row in parsed_data[1:]:
            data.append({data_keys[i]: row[i] for i, k in enumerate(row)})

        reports = []
        for item in data:
            if set(item.keys()) != {'term', 'impressions', 'clicks', 'cost', 'conversions'}:
                return Response({'detail': 'wrong file format. it should contains "term", "impressions", "clicks", '
                                           '"cost", "conversions" columns'}, status=status.HTTP_400_BAD_REQUEST)
            reports.append(Report(client_id=pk, author=request.user, **item))

        if reports:
            Report.objects.filter(client_id=pk).delete()
            Report.objects.bulk_create(reports)
            build_ngram.s(client_id=pk).apply_async()
            return Response(status=status.HTTP_200_OK)

        return Response({'detail': 'file is empty'},
                        status=status.HTTP_400_BAD_REQUEST)


class AccountTotal(mixins.AdminPermission, generics.GenericAPIView):
    def get(self, request, pk=None, *args, **kwargs):
        qs = Report.objects.filter(client_id=pk)
        return Response(Report.total(Report.sqr_annotate(pk)), status=status.HTTP_200_OK)


class DatasetTotal(mixins.AdminPermission, generics.GenericAPIView):
    def get(self, request, pk=None, *args, **kwargs):
        s = request.query_params.get('status')
        if not s:
            return Response({'detail': 'status required'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(Report.total(Report.sqr_annotate(client_id=pk, status=s)), status=status.HTTP_200_OK)


class SQRSync(mixins.AdminPermission, APIView):

    def get(self, request, *args, **kwargs):
        sync()
        return Response(status=status.HTTP_200_OK)
