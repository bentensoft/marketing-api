from django.conf.urls import url
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.authtoken import views as authtoken_views
from rest_framework import routers

admin.site.site_header = settings.ADMIN_SITE_HEADER


router = routers.DefaultRouter()


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^user/auth/', authtoken_views.obtain_auth_token),
    url(r'^admin/', admin.site.urls),
    url(r'^clients/', include('clients.urls', namespace='clients')),
    url(r'^ads/', include('ads.urls', namespace='ads')),
    url(r'^tasks/', include('tasks.urls', namespace='tasks')),
    url(r'^users/', include('profiles.urls', namespace='users')),
    url(r'^sqr/', include('sqr.urls', namespace='sqr')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
