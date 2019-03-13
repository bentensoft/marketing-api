from rest_framework import serializers
from .models import Ngram


class NgramSerializer(serializers.HyperlinkedModelSerializer):
    """Ngram Report serializer"""
    index = serializers.DecimalField(max_digits=50, decimal_places=24)
    cpa = serializers.FloatField()
    ctr = serializers.FloatField()
    cpc = serializers.FloatField()
    impressions = serializers.FloatField(source='impressions__sum')
    conversions = serializers.FloatField(source='conversions__sum')
    cost = serializers.FloatField(source='cost__sum')
    clicks = serializers.FloatField(source='clicks__sum')

    class Meta:
        model = Ngram
        fields = ('id', 'word', 'impressions', 'clicks', 'cost', 'conversions',
                  'index', 'cpa', 'ctr', 'cpc')


class NgramDetailSerializer(serializers.ModelSerializer):
    """Ngram serializer"""

    class Meta:
        model = Ngram
        fields = ('id', 'word', 'impressions', 'clicks', 'cost', 'conversions',
                  'status')
