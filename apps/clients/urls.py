from django.conf.urls import url
from django.conf.urls import include

from . import views
from tasks.views import TasksList

urlpatterns = [
    url('^$', views.ClientList.as_view(), name='clients'),
    url('^enabled/$', views.ClientEnabledList.as_view(), name='clients-enabled'),
    url('^all/$', views.ClientsListAll.as_view(), name='clients-all'),
    url('^create/$', views.ClientCreate.as_view(), name='client-create'),
    url('^(?P<pk>\d+)/update/$', views.ClientUpdate.as_view(), name='client-update'),
    url('^sync/$', views.ClientSync.as_view(), name='client-sync'),
    url('^(?P<pk>\d+)/sqr/', include('sqr.urls', namespace='sqr')),
    url('^(?P<pk>\d+)/ppr/', include('ppr.urls', namespace='ppr')),
    url('^(?P<pk>\d+)/ngram/', include('ngram.urls', namespace='ngram')),
    url('^(?P<pk>\d+)/onboarding/', include('onboarding.urls', namespace='onboarding')),
    url('^(?P<pk>\d+)/tasks/', TasksList.as_view(), name='client-tasks'),
    url('^(?P<pk>\d+)/$', views.ClientDetail.as_view(), name='client-detail'),
]
