import random
from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from twilio.rest import Client


OTP_EXPIRY_MINUTES = 5


def generate_otp():
    return str(random.randint(100000, 999999))


def get_expiry_time():
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)


def send_email_otp(email, otp):
    subject = "Verify Your Account - OTP"

    context = {
        "otp": otp,
        "expiry_minutes": OTP_EXPIRY_MINUTES,
    }

    html_message = render_to_string("emails/otp_email.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        html_message=html_message,
        fail_silently=True,  # safer for prod
    )


def send_sms_otp(mobile, otp):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    brand_name = "BookExplore"
    message_body = (
        f"{otp} is your verification code for {brand_name}. "
        f"Valid for {OTP_EXPIRY_MINUTES} minutes. "
        "Do not share this code."
    )

    client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{mobile}",
    )
