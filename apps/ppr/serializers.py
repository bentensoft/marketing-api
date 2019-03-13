from rest_framework import serializers
from profiles.serializers import UserSerializer
from .models import PPR


class PPRSerializer(serializers.HyperlinkedModelSerializer):
    """PPR serializer"""
    impressions = serializers.FloatField(source='impressions__sum', required=False)
    cost = serializers.FloatField(source='cost__sum', required=False)
    clicks = serializers.FloatField(source='clicks__sum', required=False)
    conversions = serializers.FloatField(source='conversions__sum', required=False)
    cpc = serializers.FloatField(required=False)
    cpa = serializers.FloatField(required=False)
    ctr = serializers.FloatField(required=False)
    index = serializers.FloatField(source='i', required=False)
    author = UserSerializer(required=False)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.author = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = PPR
        fields = ('id', 'placement', 'impressions', 'clicks', 'cost', 'conversions',
                  'status', 'cpc', 'cpa', 'ctr', 'index', 'modified', 'author',)
        read_only_fields = ('modified', 'auth')
