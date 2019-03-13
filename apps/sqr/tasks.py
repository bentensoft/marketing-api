from config.celery import app
from .models import Report


@app.task
def sync():
    Report.sync()
