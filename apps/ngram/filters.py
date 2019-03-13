from rest_framework import filters
from .models import Ngram


class NgramFilter(filters.FilterSet):
    """Advanced filtering for Ngram"""

    class Meta:
        model = Ngram
        fields = ['impressions']
