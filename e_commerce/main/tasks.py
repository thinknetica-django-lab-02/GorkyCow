from datetime import datetime, timedelta
from random import randrange

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.contrib.auth.models import User

from .messages import (new_goods_subscribers_notification,
                       new_goods_subscribers_weekly_notification,
                       send_sms_to_number, send_welcome_email)

logger = get_task_logger(__name__)


@shared_task
def send_welcome_email_task(user_id):
    logger.info(f"Sending welcome email to new user with id {user_id}")
    user = User.objects.get(id=user_id)
    send_welcome_email(user)


@shared_task
def send_new_goods_subscribers_notification_task(goods_id, profile_id):
    logger.info("Sending new goods email")
    profile_model = apps.get_model("main.Profile")
    profile = profile_model.objects.get(id=profile_id)
    goods_model = apps.get_model("main.Goods")
    goods = goods_model.objects.get(id=goods_id)
    new_goods_subscribers_notification(goods, profile)


@shared_task
def send_weekly_new_goods_email_task():
    logger.info("Sending new goods email")
    start_date = datetime.now() - timedelta(days=7)
    goods_model = apps.get_model("main.Goods")
    new_goods = goods_model.objects.filter(creation_date__gte=start_date)
    subscription_model = apps.get_model("main.Subscriptions")
    subscription = subscription_model.objects.get(name="New goods")
    profile_model = apps.get_model("main.Profile")

    if new_goods:
        for profile in profile_model.objects.filter(subsciber=subscription):
            new_goods_subscribers_weekly_notification(new_goods, profile)


@shared_task
def send_sms_verification_code(profile_id):
    verification_code = randrange(1000, 9999, 1)
    profile_model = apps.get_model("main.Profile")
    profile = profile_model.objects.get(id=profile_id)
    message = send_sms_to_number(
        profile.phone_number, f"Virification code: {verification_code}"
    )
    smslog_model = apps.get_model("main.SMSLog")
    smslog = smslog_model.objects.create(
        user=profile.user, code=verification_code, message=message
    )
