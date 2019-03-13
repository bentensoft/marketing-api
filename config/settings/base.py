import os
import sys
import dj_database_url
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, 'apps'))

LANGUAGES = (
    ('en', _('English')),
)

SECRET_KEY = ''

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'solo',
    'cities',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    # 'cachalot',
    'cacheops',

    'base',
    'profiles',
    'clients',
    'ads',
    'sqr',
    'ppr',
    'ngram',
    'tasks',
    'onboarding',
    'preferences',
]

CACHEOPS_REDIS = "redis://localhost:6379/1"
CACHEOPS = {
    'ads.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
    'clients.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
    'tasks.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
    'sqr.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
    'ppr.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
    'onboarding.*': {'ops': ('fetch', 'get', 'all'), 'timeout': 60*55},
}
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'config.urls'

ANYMAIL = {
    'SENDGRID_API_KEY': os.environ.get(
        'SENDGRID_API_KEY',
        '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'
    )
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL',
                               '"" <info@app.yaelconsulting.com>')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default='postgis://localhost/yaeldb'),
    'legacy': {
        'NAME': 'ady',
        'HOST': 'localhost',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': 'pppWW1000'
    }
}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tel_Aviv'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

BROKER_URL = 'amqp://guest:guest@localhost:5672/'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
SITE_ID = 1
ADMIN_SITE_HEADER = ''

handler400 = 'base.views.bad_request'
handler403 = 'base.views.forbidden'
handler404 = 'base.views.not_found'
handler500 = 'base.views.internal_error'
CSRF_FAILURE_VIEW = 'base.views.csrf_error'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAdminUser',
    # ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

GOOGLE_CREDENTIALS_JSON = os.path.join(BASE_DIR, 'credentials.json')

CACHE_HOURLY = 3600
CACHE_DAILY = 86400
