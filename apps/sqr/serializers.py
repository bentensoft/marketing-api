from rest_framework import serializers
from profiles.serializers import UserSerializer
from .models import Report


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    """SQR Report serializer"""
    impressions = serializers.FloatField(default=0.0,source='impressions__sum', required=False)
    cost = serializers.FloatField(default=0.0,source='cost__sum', required=False)
    clicks = serializers.FloatField(default=0.0,source='clicks__sum', required=False)
    conversions = serializers.FloatField(default=0.0,source='conversions__sum', required=False)
    cpc = serializers.FloatField(default=0.0, required=False)
    cpa = serializers.FloatField(default=0.0,required=False)
    ctr = serializers.FloatField(default=0.0,required=False)
    index = serializers.FloatField(default=0.0,source='i', required=False)
    author = UserSerializer(required=False)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.author = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = Report
        fields = ('id', 'term', 'impressions', 'clicks', 'cost', 'conversions',
                  'status', 'cpc', 'cpa', 'ctr', 'index', 'modified', 'author',
                  'source')
        read_only_fields = ('modified', 'auth')
