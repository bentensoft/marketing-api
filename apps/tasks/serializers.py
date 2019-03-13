from rest_framework import serializers
from profiles.serializers import UserSerializer
from profiles.serializers import UserIDSerializer
# from clients.serializers import ClientIDSerializer
from django.contrib.auth.models import User
from .models import Task
from .models import Comment
# from .models import Attachment


class CommentDetailSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'created', 'modified']


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['text', 'task']

    def create(self, validated_data):
        comment = Comment(**validated_data)
        comment.author = self.context['request'].user
        comment.save()
        return comment


class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    assignee = UserSerializer()
    watchers = UserSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    client = serializers.SerializerMethodField()

    def get_client(self, obj):
        if obj.client:
            return {
                'id': obj.client.id,
                'name': obj.client.name,
            }
        return {}

    class Meta:
        model = Task
        fields = ['user', 'name', 'body', 'client', 'is_done', 'due_date',
                  'id', 'assignee', 'watchers', 'is_recurring', 'every',
                  'comments']


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=True)
    client_id = serializers.IntegerField(required=False, allow_null=True)
    watchers = UserIDSerializer(many=True, allow_null=True)

    class Meta:
        model = Task
        fields = (
            'name',
            'assignee_id',
            'client_id',
            'watchers',
            'is_recurring',
            'is_done',
            'due_date',
            'every'
        )

    def create(self, validated_data):
        validated_data.pop('watchers')
        task = Task.objects.create(**validated_data)
        task.user = self.context['request'].user
        watchers_initial = self.get_initial()['watchers']
        watchers = User.objects.filter(id__in=[
            watcher['id'] for watcher in watchers_initial])
        for watcher in watchers:
            task.watchers.add(watcher)
        task.save()
        return task
