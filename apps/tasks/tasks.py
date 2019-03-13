import logging
from django.core.mail import send_mail
from django.utils import timezone
from django.template import Context, Template
from config.celery import app
from base.tasks import send_email
from .models import Task

logger = logging.getLogger(__name__)


@app.task
def notify_past_due():
    now = timezone.now()
    tasks = Task.objects.filter(is_done=False, due_date__lte=now)
    if not tasks.count():
        return True

    message = Template("""
    <p>Tasks passed due date:</p>

    <table style="border:1px solid #000;">
      <thead>
        <tr style="border:1px solid #000;">
          <th>Name</th>
          <th>Comments</th>
          <th>Due Date</th>
          <th>Client</th>
        </tr>
      </thead>
      <tbody>
        {% for task in tasks %}
        <tr>
            <td>{{ task.name }}</td>
            <td>{{ task.comments.count }}</td>
            <td>{{ task.due_date|date:"F m j" }}</td>
            <td>{{ task.client|default_if_none:"" }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <p>best regards,<br>
    App Yael Consulting System</p>
    """)
    context = Context({'tasks': tasks})
    send_email.apply_async(kwargs={
        'subject': '[APP] Passed Due Date',
        'message': message.render(context),
        'to': ['lior@yaelconsulting.com'],
    })
