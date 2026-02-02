import random
import threading
from datetime import timedelta

from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from .models import OTP


OTP_RESEND_COOLDOWN = 120  # seconds
OTP_EXPIRY_MINUTES = 5


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def get_expiry_time():
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)


# -------------------- EMAIL (ASYNC) --------------------


def _send_email_otp_sync(email: str, otp: str) -> None:
    subject = "Verify Your Account - OTP"
    context = {"otp": otp, "expiry_minutes": OTP_EXPIRY_MINUTES}

    html_message = render_to_string("emails/otp_email.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=True,  # set False if you want errors in logs
    )


def send_email_otp(email: str, otp: str) -> None:
    """Async email sender (thread)."""
    threading.Thread(
        target=_send_email_otp_sync,
        args=(email, otp),
        daemon=True,
    ).start()


# -------------------- SMS (ASYNC) --------------------


def _send_sms_otp_sync(mobile: str, otp: str) -> None:
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


def send_sms_otp(mobile: str, otp: str) -> None:
    """Async SMS sender (thread)."""
    threading.Thread(
        target=_send_sms_otp_sync,
        args=(mobile, otp),
        daemon=True,
    ).start()


# -------------------- COOLDOWN CHECK --------------------


def check_otp_resend_cooldown(filters) -> None:
    """
    Enforces resend cooldown.
    Uses settings.OTP_RESEND_COOLDOWN if present, otherwise OTP_RESEND_COOLDOWN.
    """
    cooldown = getattr(settings, "OTP_RESEND_COOLDOWN", OTP_RESEND_COOLDOWN)

    last_otp = OTP.objects.filter(**filters).order_by("-created_at").first()
    if not last_otp:
        return

    diff = (timezone.now() - last_otp.created_at).total_seconds()
    if diff < cooldown:
        remaining = int(cooldown - diff)
        raise serializers.ValidationError(
            f"Please wait {remaining} seconds before resending OTP."
        )
