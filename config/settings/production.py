import os
import raven
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

RAVEN_CONFIG = {
    'dsn': os.environ['SENTRY_DSN'],
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': 'localhost:6379',
#     },
# }

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
