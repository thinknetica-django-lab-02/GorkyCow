from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.contrib.auth.models import User

from .messages import send_welcome_email, new_goods_subscribers_notification


logger = get_task_logger(__name__)



@shared_task
def send_welcome_email_task(user_id):
    logger.info(f"Sending welcome email to new user with id {user_id}")
    user = User.objects.get(id=user_id)
    send_welcome_email(user)


@shared_task
def send_new_goods_subscribers_notification_task(goods_id, profile_id):
    logger.info("Sent new goods email")
    profile_model = apps.get_model("main.Profile")
    profile = profile_model.objects.get(id=profile_id)
    goods_model = apps.get_model("main.Goods")
    goods = goods_model.objects.get(id=goods_id)
    new_goods_subscribers_notification(goods, profile)
