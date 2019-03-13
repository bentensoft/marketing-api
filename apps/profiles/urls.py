from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.UsersList.as_view(), name='users-list'),
]
