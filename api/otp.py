import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from_ = (settings.TWILIO_PHONE_NUMBER,)
from_ = (settings.TWILIO_ACCOUNT_SID,)
form_ = (settings.TWILIO_AUTH_TOKEN,)


def generate_otp():
    return str(random.randint(100000, 999999))


def get_expiry_time():
    return timezone.now() + timedelta(minutes=2)


def send_email_otp(email, otp):
    subject = "Verify Your Account - OTP"

    context = {"otp": otp}
    html_message = render_to_string("emails/otp_email.html", context)

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=False,
    )
    print(f"Professional HTML Email sent to {email}")


def send_sms_otp(mobile, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    brand_name = "BookExplore"
    message_body = f"{otp} is your verification code for {brand_name}. For security, do not share this code. Valid for 2 mins."

    client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{mobile}",
    )
    print(f"SMS OTP sent to {mobile}")
