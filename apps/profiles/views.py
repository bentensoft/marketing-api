from django.contrib.auth.models import User
from rest_framework import generics
from . import serializers
from base import mixins


class UsersList(mixins.AdminPermission, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
