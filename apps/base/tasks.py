import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags
from config.celery import app

logger = logging.getLogger(__name__)


@app.task()
def send_email(subject, message, to=[], *args, **kwargs):
    """Send email to the user"""
    logger.info(subject, message, to, args, kwargs)
    send_mail(subject=subject, message=strip_tags(message),
              html_message=message, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=to, fail_silently=False)
