from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse_lazy
from twilio.rest import Client


def send_welcome_email(user):
    subject = "Welcome to Bomzhon.com!"
    text_content = f"{user.get_username}, welcome to Bomzhone.com!"
    ctx = {"title": subject, "user_name": user.get_username}
    html_content = get_template("messages/welcome.html").render(ctx)
    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def new_goods_subscribers_notification(goods, profile):
    subject = "Новый товар в Bomzhon!"
    ctx = {
        "title": subject,
        "user_name": profile.user.get_username(),
        "goods_name": goods.name,
        "goods_description": goods.description,
        "goods_id": goods.id,
    }
    html_message = get_template(
        "account/email/new_goods_email.html"
    ).render(ctx)
    url = reverse_lazy("goods-detail", kwargs={"pk": goods.id})
    text_content = f"Привет, {profile.user.get_username()}! "
    + f"В Bomzhon появился новый товар. Подробности по ссылке: {url}"
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [profile.user.email]
    )
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def new_goods_subscribers_weekly_notification(goods, profile):
    subject = "Новые товары в Bomzhon!"
    ctx = {
        "title": subject,
        "user_name": profile.user.get_username(),
        "new_goods": goods,
    }
    html_message = get_template(
        "account/email/new_goods_email_weekly.html"
    ).render(ctx)
    url = reverse_lazy("goods")
    text_content = f"Привет, {profile.user.get_username()}! "
    + f"В Bomzhon появились новые товары. Подробности по ссылке: {url}"
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [profile.user.email]
    )
    msg.attach_alternative(html_message, "text/html")
    msg.send()


def send_sms_to_number(to_number, sms_text):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOCKEN)
    message = client.messages.create(
        body=sms_text, from_=settings.TWILIO_PHONE_NUMBER, to=to_number
    )
    return message
