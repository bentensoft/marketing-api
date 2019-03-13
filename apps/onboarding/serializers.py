from rest_framework import serializers
from .models import Channel
from .models import Assignment


class AssignmentSerializer(serializers.HyperlinkedModelSerializer):
    """Assignment Serializer"""
    channel = serializers.SerializerMethodField()
    last_changed_by = serializers.SerializerMethodField()

    def get_channel(self, obj):
        return obj.channel_id

    def get_last_changed_by(self, obj):
        log = obj.log()
        if log:
            return log.user.username
        return None

    class Meta:
        model = Assignment
        fields = ('id', 'channel', 'name', 'notes', 'order', 'status',
                  'modified', 'last_changed_by')
        read_only_fields = ('id',)


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    """Channel Serializer"""
    assignments = serializers.SerializerMethodField()

    def get_assignments(self, channel):
        assignments = channel.assignments.filter(
            client_id=self.context.get('pk'))
        serializer = AssignmentSerializer(instance=assignments, many=True,
                                          context=self.context)
        return serializer.data

    class Meta:
        model = Channel
        fields = ('id', 'name', 'logo', 'order', 'assignments')
        read_only_fields = ('id',)
