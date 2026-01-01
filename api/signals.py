from decouple import config
from .models import CustomUser
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save, post_delete, pre_save

ADMIN_EMAIL = config("ADMIN_EMAIL")
ADMIN_PHONE = config("ADMIN_PHONE")
SITE_NAME = config("SITE_NAME")

import threading


def send_email_async(email_message):
    def _send():
        try:
            email_message.send()
        except Exception as e:
            print("Email send failed:", e)

    threading.Thread(target=_send, daemon=True).start()


@receiver(post_save, sender=CustomUser)
def user_created_email(sender, instance, created, **kwargs):
    if not created:
        return

    # -------- USER EMAIL --------
    context = {
        "user": instance,
        "SITE_NAME": SITE_NAME,
        "ADMIN_EMAIL": ADMIN_EMAIL,
        "ADMIN_PHONE": ADMIN_PHONE,
    }

    # -------- USER EMAIL --------
    user_html = render_to_string(
        "emails/user_registered.html",
        context,
    )

    sendToUser = EmailMultiAlternatives(
        subject="Your account is created 🎉",
        body="Your account has been created.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[instance.email],
    )
    sendToUser.attach_alternative(user_html, "text/html")
    send_email_async(sendToUser)

    # -------- ADMIN EMAIL --------
    admin_html = render_to_string(
        "emails/admin_user_registered.html",
        {
            "user": instance,
            "SITE_NAME": SITE_NAME,
            "ADMIN_EMAIL": ADMIN_EMAIL,
            "ADMIN_PHONE": ADMIN_PHONE,
        },
    )

    sendToAdmin = EmailMultiAlternatives(
        subject="New User Registered",
        body="A new user registered.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ADMIN_EMAIL],
    )
    sendToAdmin.attach_alternative(admin_html, "text/html")
    send_email_async(sendToAdmin)


@receiver(post_delete, sender=CustomUser)
def user_deleted_email(sender, instance, **kwargs):

    # -------- USER EMAIL --------
    user_html = render_to_string(
        "emails/user_deleted.html",
        {
            "user": instance,
            "SITE_NAME": SITE_NAME,
            "ADMIN_EMAIL": ADMIN_EMAIL,
            "ADMIN_PHONE": ADMIN_PHONE,
        },
    )

    deleteToUser = EmailMultiAlternatives(
        subject="Your account has been deleted",
        body="Your account has been deleted.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[instance.email],
    )
    deleteToUser.attach_alternative(user_html, "text/html")
    if instance.email:
        send_email_async(deleteToUser)

    # -------- ADMIN EMAIL --------
    admin_html = render_to_string(
        "emails/admin_user_deleted.html",
        {
            "user": instance,
            "SITE_NAME": SITE_NAME,
            "ADMIN_EMAIL": ADMIN_EMAIL,
            "ADMIN_PHONE": ADMIN_PHONE,
        },
    )

    deleteToAdmin = EmailMultiAlternatives(
        subject="User Account Deleted",
        body="A user account was deleted.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ADMIN_EMAIL],
    )
    deleteToAdmin.attach_alternative(admin_html, "text/html")
    send_email_async(deleteToAdmin)


from .models import Author


@receiver(pre_save, sender=Author)
def author_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Author.objects.get(pk=instance.pk)
            instance._old_is_verified = old.is_verified
        except Author.DoesNotExist:
            instance._old_is_verified = None
    else:
        instance._old_is_verified = None


@receiver(post_save, sender=Author)
def author_verification_status_email(sender, instance, created, **kwargs):
    print("AUTHOR SIGNAL FIRED:", instance.pk, instance.is_verified)

    if created:
        return

    old = getattr(instance, "_old_is_verified", None)
    new = instance.is_verified

    # -------- VERIFIED --------
    if old is False and new is True:
        user = instance.user

        html = render_to_string(
            "emails/author_verified.html",
            {
                "user": user,
                "author": instance,
                "SITE_NAME": SITE_NAME,
                "ADMIN_EMAIL": ADMIN_EMAIL,
                "ADMIN_PHONE": ADMIN_PHONE,
            },
        )

        mail = EmailMultiAlternatives(
            subject="You are now a verified author 🎉",
            body="Your author profile has been verified.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        mail.attach_alternative(html, "text/html")
        send_email_async(mail)

    # -------- REJECTED --------
    elif old is True and new is False:
        user = instance.user

        html = render_to_string(
            "emails/author_rejected.html",
            {
                "user": user,
                "author": instance,
                "SITE_NAME": SITE_NAME,
                "ADMIN_EMAIL": ADMIN_EMAIL,
                "ADMIN_PHONE": ADMIN_PHONE,
            },
        )

        mail = EmailMultiAlternatives(
            subject="Author Profile Rejected",
            body="Your author profile was rejected.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        mail.attach_alternative(html, "text/html")
        send_email_async(mail)
