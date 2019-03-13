import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Client
from . import serializers
from base import mixins


class TimeFrameMixin(object):

    def get_timeframe(self):
        now = timezone.now()
        default = '{month}-{year}'.format(month=now.month, year=now.year)
        timeframe = self.request.GET.get('timeframe', default)
        try:
            return datetime.datetime.strptime(timeframe, '%m-%Y')
        except ValueError:
            return now

    def get_serializer_context(self):
        context = super().get_serializer_context()
        timeframe = self.get_timeframe()
        context.update({
            'created__month': timeframe.month,
            'created__year': timeframe.year
        })
        return context


class ClientList(TimeFrameMixin, mixins.AdminPermission, generics.ListAPIView):
    queryset = Client.objects.filter(is_enabled=True)
    serializer_class = serializers.ClientSerializer

    def cache_key(self):
        return 'client-list-{timeframe}'.format(
            timeframe=self.request.GET.get('timeframe'))

    def list(self, request, *args, **kwargs):
        queryset = cache.get(self.cache_key())
        if not queryset:
            masters = set(Client.objects.values_list('master', flat=True))
            null_masters = Client.objects.filter(master__isnull=True)\
                                 .values_list('id', flat=True)
            [masters.add(master) for master in null_masters]

            queryset = Client.objects.exclude(is_enabled=False)\
                                     .filter(id__in=masters)
            cache.set(self.cache_key(), queryset, settings.CACHE_HOURLY)

        if request.user.username == 'facebookuser':
            queryset = queryset.filter(name__icontains='Yael')

        serializer = serializers.MasterSerializer(
            queryset, many=True, context=self.get_serializer_context())
        return Response({'data': serializer.data})


class ClientDetail(TimeFrameMixin, mixins.AdminPermission,
                   generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.filter(is_enabled=True)
    serializer_class = serializers.ClientDetailSerializer


class ClientsListAll(TimeFrameMixin, mixins.AdminPermission,
                     generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = serializers.ClientDetailSerializer
    pagination_class = None


class ClientEnabledList(TimeFrameMixin, mixins.AdminPermission,
                        generics.ListAPIView):
    queryset = Client.objects.filter(is_enabled=True)
    serializer_class = serializers.ClientDetailSerializer


class ClientCreate(mixins.AdminPermission, generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = serializers.ClientCreateSerializer


class ClientUpdate(mixins.AdminPermission, generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = serializers.ClientDetailSerializer


class ClientSync(mixins.AdminPermission, APIView):
    queryset = Client.objects.none()

    def get(self, request, *args, **kwargs):
        Client.sync.all()
        return Response(status=status.HTTP_200_OK)
