import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import sync
from base import mixins


class AdsSync(mixins.AdminPermission, APIView):

    def get(self, request, *args, **kwargs):
        sync()
        return Response(status=status.HTTP_200_OK)
