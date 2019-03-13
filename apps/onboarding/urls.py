from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.Assignments.as_view(), name='assignments'),
    url('^channels/$', views.Channels.as_view(), name='channels-list'),
    url('^(?P<assignment_pk>.+)$', views.AssignmentDetail.as_view(),
        name='assignment-detail'),
]
