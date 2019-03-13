from rest_framework import generics
from . import serializers
from base import mixins
from .models import Task
from .models import Comment


class TasksList(mixins.AdminPermission, generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        kwargs = {}
        pk = self.kwargs.get('pk')
        if pk:
            kwargs['client__id'] = int(pk)
        return self.queryset.filter(**kwargs)


class TaskDetail(mixins.AdminPermission, generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer


class TaskCreate(mixins.AdminPermission, generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskCreateSerializer


class CommentCreate(mixins.AdminPermission, generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentCreateSerializer
