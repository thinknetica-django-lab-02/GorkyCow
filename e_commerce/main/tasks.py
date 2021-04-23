from datetime import datetime, timedelta
from random import randrange

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.cache import cache
from django.db import transaction

from .messages import (new_goods_subscribers_notification,
                       new_goods_subscribers_weekly_notification,
                       send_sms_to_number, send_welcome_email)

logger = get_task_logger(__name__)


@shared_task
def send_welcome_email_task(user_id):
    logger.info(f"Sending welcome email to new user with id {user_id}")
    user_model = apps.get_model("auth.User")
    user = user_model.objects.get(id=user_id)
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
    logger.info(
        f"Sending verification code via SMS to number: {profile.phone_number}"
    )
    message = send_sms_to_number(
        profile.phone_number, f"Virification code: {verification_code}"
    )
    smslog_model = apps.get_model("main.SMSLog")
    smslog_model.objects.create(
        user=profile.user, code=verification_code, message=message
    )


@shared_task
def save_views_counter_cached_values_task():
    logger.info("Saving goods views counters to DB")
    goods_model = apps.get_model("main.Goods")
    goods_ids = list(goods_model.objects.all().values_list("id", flat=True))
    cache_keys = [f"views_counter_{gid}" for gid in goods_ids]
    cache_values = cache.get_many(cache_keys)
    with transaction.atomic():
        for key, value in cache_values.items():
            goods = goods_model.objects.get(
                id=int(key.replace("views_counter_", ""))
            )
            goods.views_counter = value
            goods.save()
    logger.info("Saved goods views counters successfully")
