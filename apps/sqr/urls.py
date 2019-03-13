from django.conf.urls import url

from . import views

urlpatterns = [
    url('^(?P<sqr_pk>\d+)/$', views.SQRDetail.as_view(), name='sqr-detail'),
    url('^$', views.SQRList.as_view(), name='sqr'),
    url('^old/$', views.SQRListOld.as_view(), name='sqr'),
    url('^upload/', views.SQRUploadCSV.as_view(), name='sqr-upload-csv'),
    url('^spreadsheet/', views.SQRLoadFromGoogleSpreadsheet.as_view(), name='sqr-spreadsheet'),
    url('^account-total/', views.AccountTotal.as_view(), name='sqr-account-total'),
    url('^dataset-total/', views.DatasetTotal.as_view(), name='sqr-dataset-total'),
    url('^sync/$', views.SQRSync.as_view(), name='sqr-sync'),
]
