from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from raven import Client
from raven.contrib.celery import register_signal
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')


if hasattr(settings, 'RAVEN_CONFIG'):
    client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
    register_signal(client)


app = Celery('config', backend='redis://localhost')
app.config_from_object('django.conf:settings', namespace="App")
app.autodiscover_tasks()
TASK_SERIALIZER = 'json'
ACCEPT_CONTENT = ['json']

app.conf.beat_schedule = {
    'ads': {
        'task': 'ads.tasks.sync',
        'schedule': crontab(minute='*/60'),
        'args': None,
    },
    'sqr': {
        'task': 'sqr.tasks.sync',
        'schedule': crontab(minute=0, hour=8),
        'args': None,
    },
    'ngram': {
        'task': 'ngram.tasks.sync',
        'schedule': crontab(minute=0, hour=9),
        'args': None
    },
    'ppr': {
        'task': 'ppr.tasks.sync',
        'schedule': crontab(minute=0, hour=8),
        'args': None
    },
    'tasks-notify-passed-due-date': {
        'task': 'tasks.tasks.notify_past_due',
        'schedule': crontab(minute=0, hour=8),
        'args': None
    }
}
