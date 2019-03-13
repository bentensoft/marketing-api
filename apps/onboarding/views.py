from rest_framework import generics
from base import mixins
from . import serializers
from .models import Assignment
from .models import Channel


class Assignments(mixins.AdminPermission, generics.ListAPIView):
    queryset = Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer

    def get_pk(self):
        return int(self.kwargs.get('pk'))

    def get_queryset_kwargs(self):
        kwargs = super().get_queryset_kwargs()
        kwargs.update({
            'client_id': self.get_pk()
        })
        return kwargs


class AssignmentDetail(mixins.AdminPermission,
                       generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'assignment_pk'
    queryset = Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer


class Channels(mixins.AdminPermission, generics.ListAPIView):
    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'pk': int(self.kwargs.get('pk'))
        })
        return context
