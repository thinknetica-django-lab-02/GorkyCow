import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from main.messages import new_goods_subscribers_weekly_notification
from main.models import Goods, Profile, Subscriptions

logger = logging.getLogger(__name__)


def send_new_goods_weekly_schedule():
    start_date = datetime.now() - timedelta(days=7)
    new_goods = Goods.objects.filter(creation_date__gte=start_date)

    subscription = Subscriptions.objects.get(name="New goods")
    for profile in Profile.objects.filter(subsciber=subscription):
        new_goods_subscribers_weekly_notification(new_goods, profile)


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job
    executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_new_goods_weekly_schedule,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="send_new_goods_weekly_schedule",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job 'send_new_goods_weekly_schedule'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
