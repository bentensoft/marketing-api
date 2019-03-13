from django.conf.urls import url
from django.conf.urls import include

from . import views


urlpatterns = [
    url('^sync/$', views.AdsSync.as_view(), name='ads-sync'),
]
