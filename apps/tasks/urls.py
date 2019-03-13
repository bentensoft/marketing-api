from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.TasksList.as_view(), name='tasks-list'),
    url('^(?P<pk>\d+)/$', views.TaskDetail.as_view(), name='tasks-detail'),
    url('^comment/$', views.CommentCreate.as_view(), name='comment-create'),
    url('^create/$', views.TaskCreate.as_view(), name='tasks-create'),
]
