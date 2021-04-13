from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


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
