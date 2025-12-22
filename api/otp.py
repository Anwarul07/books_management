import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from_ = settings.TWILIO_PHONE_NUMBER, 
from_ = settings.TWILIO_ACCOUNT_SID,    
form_= settings.TWILIO_AUTH_TOKEN, 


def generate_otp():
    return str(random.randint(100000, 999999))


def get_expiry_time():
    return timezone.now() + timedelta(minutes=2)


def send_email_otp(email, otp):
    subject = "Your OTP for Registration"
    message = f"Your OTP is {otp}. It is valid for 2 minutes."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    print(f"EMAIL OTP to {email}: {otp}")


def send_sms_otp(mobile, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    client.messages.create(
        body=f"Your OTP is {otp}. Valid for 2 minutes.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{mobile}",  # India example
    )
    print(f"SMS OTP to {mobile}: {otp}")
