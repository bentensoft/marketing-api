import codecs
import csv

import chardet
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from cities.models import Country
from rest_framework.views import APIView

from .models import PPR
from . import serializers
from base import mixins
from base.parsers import SearchParser
from ngram.tasks import build_ngram


class PPRList(mixins.AdminPermission, generics.ListAPIView):
    serializer_class = serializers.PPRSerializer

    def get_pk(self):
        return int(self.kwargs.get('pk'))

    def get_status(self):
        return self.request.GET.get('status', PPR.ACTIVE)

    def get_queryset_kwargs(self):
        kwargs = {
            'client_id': self.get_pk(),
            'status': self.get_status()
        }

        return kwargs

    def get_filters(self):
        raw = self.request.GET.get('filters', None)
        predefined = None
        # TODO refactor this if-for-if shit later
        if raw:
            for item in raw.split(','):
                if item == 'countries':
                    countries = Country.objects.values_list('name', flat=True)
                    for country in countries:
                        q = Q(placement__icontains=country)
                        predefined = (predefined and (predefined | q)) or q
                elif item == 'usa_states':
                    states = Country.objects.get(name='United States')\
                                    .regions.values_list('name', flat=True)
                    for state in states:
                        q = Q(placement__icontains=state)
                        predefined = (predefined and (predefined | q)) or q
                elif item == 'top_usa_cities':
                    cities = Country.objects.get(name='United States')\
                                    .cities.order_by('-population')[:400]
                    for city in cities:
                        q = Q(placement__icontains=city)
                        predefined = (predefined and (predefined | q)) or q

        return predefined

    def get_order_by(self):
        return self.request.GET.get('sortBy', '-placement')

    def get_queryset(self):
        search = SearchParser(PPR, self.request.GET.get('q', ''), 'placement')
        qs = search.get_queryset(**self.get_queryset_kwargs())
        filters = self.get_filters()
        if filters:
            qs = qs.filter(filters)
        qs = PPR.ppr_annotate(qs=qs)
        if qs:
            return qs.order_by(self.get_order_by())
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        context = {
            'request': request,
        }

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context=context)
            response = self.get_paginated_response(serializer.data)
            search_total = PPR.total(queryset)
            response.data.update({'search_total': search_total})
            return response


class PPRDetail(mixins.AdminPermission, generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'ppr_pk'
    queryset = PPR.objects.all()
    serializer_class = serializers.PPRSerializer


class PPRUploadCSV(mixins.AdminPermission, APIView):
    def post(self, request, pk=None, *args, **kwargs):
        if not request.FILES:
            return Response({'detail': 'file required'}, status=status.HTTP_400_BAD_REQUEST)

        if not next(iter(request.FILES.keys())).endswith(".csv"):
            return Response({'detail': 'csv file expected'})

        file_obj = next(iter(request.FILES.values()))
        data = csv.DictReader(codecs.iterdecode(file_obj, chardet.detect(file_obj.read())['encoding']))

        pprs = []
        for item in data:
            if set(item.keys()) != {'placement', 'impressions', 'clicks', 'cost', 'conversions'}:
                return Response({'detail': 'wrong file format. it should contains "placement", "impressions", '
                                           '"clicks", "cost", "conversions" columns'},
                                status=status.HTTP_400_BAD_REQUEST)
            pprs.append(PPR(client_id=pk, author=request.user, **item))

        if pprs:
            PPR.objects.filter(client_id=pk).delete()
            PPR.objects.bulk_create(pprs)
            build_ngram.s(client_id=pk).apply_async()
            return Response(status=status.HTTP_200_OK)

        return Response({'detail': 'file is empty'}, status=status.HTTP_400_BAD_REQUEST)


class PPRLoadFromGoogleSpreadsheet(mixins.AdminPermission, APIView):
    def post(self, request, pk=None, *args, **kwargs):
        from clients.models import Client
        client = get_object_or_404(Client.objects.all(), pk=pk)
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.GOOGLE_CREDENTIALS_JSON, scope)
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
            if set(item.keys()) != {'placement', 'impressions', 'clicks', 'cost', 'conversions'}:
                return Response({'detail': 'wrong file format. it should contains "placement", "impressions", "clicks", '
                                           '"cost", "conversions" columns'}, status=status.HTTP_400_BAD_REQUEST)
            reports.append(PPR(client_id=pk, author=request.user, **item))

        if reports:
            PPR.objects.filter(client_id=pk).delete()
            PPR.objects.bulk_create(reports)
            build_ngram.s(client_id=pk).apply_async()
            return Response(status=status.HTTP_200_OK)

        return Response({'detail': 'file is empty'}, status=status.HTTP_400_BAD_REQUEST)


class AccountTotal(mixins.AdminPermission, generics.GenericAPIView):
    def get(self, request, pk=None, *args, **kwargs):
        return Response(PPR.total(PPR.ppr_annotate(pk)), status=status.HTTP_200_OK)


class DatasetTotal(mixins.AdminPermission, generics.GenericAPIView):
    def get(self, request, pk=None, *args, **kwargs):
        s = request.query_params.get('status')
        if not s:
            return Response({'detail': 'status required'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PPR.total(PPR.ppr_annotate(client_id=pk, status=s)), status=status.HTTP_200_OK)
