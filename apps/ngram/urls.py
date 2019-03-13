from django.conf.urls import url
from django.conf.urls import include

from . import views

urlpatterns = [
    url('^$', views.NgramList.as_view(), name='ngram-list'),
    url('^(?P<ngram_pk>\d+)/$', views.NgramDetail.as_view(),
        name='ngram-detail'),
]
