from config.celery import app
from .models import Ad


@app.task
def sync():
    Ad.sync()
