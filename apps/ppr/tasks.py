from config.celery import app
from .models import PPR


@app.task
def sync():
    PPR.sync()
