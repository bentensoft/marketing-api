from django.conf.urls import url

from . import views

urlpatterns = [
    url('^(?P<ppr_pk>\d+)/$', views.PPRDetail.as_view(), name='ppr-detail'),
    # url('^total/$', views.AccountTotal.as_view(), name='account-total'),
    url('^$', views.PPRList.as_view(), name='ppr'),
    url('^upload/', views.PPRUploadCSV.as_view(), name='ppr-upload-csv'),
    url('^spreadsheet/', views.PPRLoadFromGoogleSpreadsheet.as_view(), name='ppr-spreadsheet'),
    url('^account-total/', views.AccountTotal.as_view(), name='ppr-account-total'),
    url('^dataset-total/', views.DatasetTotal.as_view(), name='ppr-dataset-total'),
]
