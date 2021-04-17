import os

from celery import Celery
from celery.schedules import crontab

# from main.tasks import send_weekly_new_goods_email_task


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_commerce.settings")

app = Celery("e_commerce")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_weekly_new_goods_email_task": {
        "task": "main.tasks.send_weekly_new_goods_email_task",
        # "schedule": crontab(hour=1, minute=21, day_of_week="sunday"),
        "schedule": crontab(minute="*/1"),
    },
}
