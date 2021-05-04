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
    """This function gets a User object by a provided id and sends to them
    a welcome email. Runs as a delayed task.

    :param user_id: id of a user in DB
    :type user_id: int
    """
    logger.info(f"Sending welcome email to new user with id {user_id}")
    user_model = apps.get_model("auth.User")
    user = user_model.objects.get(id=user_id)
    send_welcome_email(user)


@shared_task
def send_new_goods_subscribers_notification_task(goods_id, profile_id):
    """This function gets Goods and Profile objects by a provided IDs and
    sends to them an email about these Goods. Runs as a delayed task.

    :param goods_id: id of a goods in DB
    :type goods_id: int
    :param profile_id: id of a profile in DB
    :type profile_id: int
    """
    logger.info("Sending new goods email")
    profile_model = apps.get_model("main.Profile")
    profile = profile_model.objects.get(id=profile_id)
    goods_model = apps.get_model("main.Goods")
    goods = goods_model.objects.get(id=goods_id)
    new_goods_subscribers_notification(goods, profile)


@shared_task
def send_weekly_new_goods_email_task():
    """This function sends an email about new goods which was added this week
    to subscribed users. Runs as a scheduled task.
    """
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
    """This function generates a confirmation 4-digit code, sends it to
    a provided user, and saves a server's response to a DB. Runs as a
    delayed task.

    :param profile_id: id of a profile in DB
    :type profile_id: int
    """
    verification_code = randrange(1000, 9999, 1)
    profile_model = apps.get_model("main.Profile")
    profile = profile_model.objects.get(id=profile_id)
    logger.info(f"Sending verification code via SMS to number: {profile.phone_number}")
    message = send_sms_to_number(
        profile.phone_number, f"Virification code: {verification_code}"
    )
    smslog_model = apps.get_model("main.SMSLog")
    smslog_model.objects.create(
        user=profile.user, code=verification_code, message=message
    )


@shared_task
def save_views_counter_cached_values_task():
    """This function gets goods views counters from a cache and saves them
    to DB. Runs as a scheduled task.
    """
    logger.info("Saving goods views counters to DB")
    goods_model = apps.get_model("main.Goods")
    goods_ids = list(goods_model.objects.all().values_list("id", flat=True))
    cache_keys = [f"views_counter_{gid}" for gid in goods_ids]
    cache_values = cache.get_many(cache_keys)
    with transaction.atomic():
        for key, value in cache_values.items():
            goods = goods_model.objects.get(id=int(key.replace("views_counter_", "")))
            goods.views_counter = value
            goods.save()
    logger.info("Saved goods views counters successfully")


@shared_task
def create_new_tags_task(tags_list):
    """This function checks if tags exist and create it if not

    :param tags_list: tags
    :type tags_list: List
    """
    logger.info("Start task: create_new_tags_task")
    tags_model = apps.get_model("main.Tag")
    for tag_name in tags_list:
        tags_model.objects.get_or_create(name=tag_name)
    logger.info("Finish task: create_new_tags_task")
