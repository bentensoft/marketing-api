from rest_framework import generics
from rest_framework import pagination
from django.db.models.aggregates import Sum
from django.db.models import F, ExpressionWrapper
from django.db.models import Case, When, Value
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from . import serializers
from .models import Ngram
# from .filters import NgramFilter
from base import mixins
from clients.models import Client


class NgramPagination(pagination.PageNumberPagination):
    page_size = 10


class NgramList(mixins.AdminPermission, generics.ListAPIView):
    serializer_class = serializers.NgramSerializer
    pagination_class = NgramPagination
    filter_backends = (DjangoFilterBackend,)
    # TODO later
    # filter_class = NgramFilter

    def get_pk(self):
        return int(self.kwargs.get('pk'))

    def get_order_by(self):
        raw = self.request.GET.get('sortBy', '-impressions')

        if raw.startswith('-'):
            value = raw[1:]
            order = '-'
        else:
            value = raw
            order = ''

        mapper = {
            'impressions': 'impressions__sum',
            'cpa': 'cpa',
            'cost': 'cost__sum',
            'cpc': 'cpc',
            'click': 'clicks__sum',
            'conversions': 'conversions__sum',
            'ctr': 'ctr',
            'index': 'index',
        }
        return order + mapper.get(value, 'impressions')

    def get_queryset_kwargs(self):
        return {
            'client': self.get_client(),
            'status': self.request.GET.get('status', Ngram.ACTIVE)
        }

    def get_after_annotate_kwargs(self):
        kwargs = {}
        # NOTICE filtering happens here
        filter_mapper = {
            'impressions': 'impressions__sum',
            'cost': 'cost__sum',
            'conversions': 'conversions__sum',
            'clicks': 'clicks__sum',
            'cpa': 'cpa',
            'ctr': 'ctr',
            'cpc': 'cpc',
            'index': 'index'
        }

        for key in self.request.GET.keys():
            for item in filter_mapper.keys():
                if key.startswith(item):
                    kwargs[key] = self.request.GET.get(key)

        return kwargs

    def get_client(self):
        return Client.objects.get(id=self.get_pk())

    def get_queryset(self):
        data_total = Ngram.data_total(self.get_client())
        kwargs = self.get_queryset_kwargs()
        return Ngram.objects.filter(**kwargs).values('word', 'id').annotate(
            Sum('impressions'),
            Sum('cost'),
            Sum('clicks'),
            Sum('conversions'),
            cpc=Case(
                When(clicks__sum=0, then=Value(0)),
                default=ExpressionWrapper(
                    F('cost__sum') / F('clicks__sum'),
                    models.FloatField()),
                output_field=models.FloatField()
            ),
            ctr=Case(
                When(impressions__sum=0, then=Value(0)),
                default=ExpressionWrapper(
                    F('clicks__sum') * 100 / F('impressions__sum'),
                    models.FloatField()),
                output_field=models.FloatField()
            ),
            cpa=Case(
                When(conversions__sum=0, then=Value(0)),
                default=ExpressionWrapper(
                    F('cost__sum') / F('conversions__sum'),
                    models.FloatField()),
                output_field=models.FloatField()
            ),
            index=ExpressionWrapper(
                F('impressions__sum') / (data_total['clicks__sum'] or 1) +
                F('clicks__sum') / (data_total['ctr'] or 1) +
                F('cost__sum') / (data_total['conversions__sum'] or 1) +
                F('conversions__sum') / (data_total['cpa'] or 1),
                models.DecimalField(max_digits=50, decimal_places=24)),
        ).filter(**self.get_after_annotate_kwargs())\
         .order_by(self.get_order_by())

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)


class NgramDetail(mixins.AdminPermission,
                  generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'ngram_pk'
    queryset = Ngram.objects.all()
    serializer_class = serializers.NgramDetailSerializer
