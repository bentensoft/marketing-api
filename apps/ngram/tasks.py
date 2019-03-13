from config.celery import app
from clients.models import Client
from .parsers import NgramParser


@app.task
def build_ngram(client_id):
    """Build ngram for the particular client"""
    NgramParser(Client.objects.get(id=client_id)).process()
    return True


@app.task
def sync():
    clients = Client.objects.filter(is_enabled=True)
    for client in clients:
        build_ngram.s(client_id=client.id).apply_async()
    return True
