from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = "Templates layout check karne ke liye testing command"

    def handle(self, *args, **options):
        # Fake User Data for Testing
        class MockUser:
            def __init__(self):
                self.username = config("test_username")
                self.email = config("test_email")
                self.mobile = config("test_mobile")
                self.role = config("test_role")
                self.profile = config("test_profile")

        user_instance = MockUser()

        # Context matching your signals
        context = {
            "user": user_instance,
            "ADMIN_PHONE": config("ADMIN_PHONE"),
            "SITE_NAME": config("SITE_NAME"),
            "ADMIN_EMAIL": config("ADMIN_EMAIL"),
            "date": "December 21, 2025",  # Fixed date for testing
        }

        # Templates List
        templates = [
            # {
            #     "name": "Welcome",
            #     "file": "emails/user_registered.html",
            #     "sub": "Welcome to Bookselling 🎉",
            # },
            # {
            #     "name": "Deleted",
            #     "file": "emails/user_deleted.html",
            #     "sub": "Account Deleted Notice",
            # },
            {
                "name": "Admin New User",
                "file": "emails/admin_user_registered.html",
                "sub": "Welcome to Bookselling 🎉",
            },
            {
                "name": " Admin Deleted",
                "file": "emails/admin_user_deleted.html",
                "sub": "Account Deleted Notice",
            },
            # {
            #     "name": "Verified",
            #     "file": "emails/author_verified.html",
            #     "sub": "You are Verified 🎉",
            # },
            # {
            #     "name": "Rejected",
            #     "file": "emails/author_rejected.html",
            #     "sub": "Profile Update Required",
            # },
        ]

        self.stdout.write("Testing shuru ho rahi hai...")

        for t in templates:
            try:
                html_content = render_to_string(t["file"], context)
                mail = EmailMultiAlternatives(
                    subject=f"[TEST] {t['sub']}",
                    body="Please open in HTML view.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=config("ADMIN_EMAIL"),
                )
                mail.attach_alternative(html_content, "text/html")
                mail.send()
                self.stdout.write(self.style.SUCCESS(f"Bheja gaya: {t['name']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in {t['name']}: {e}"))

        self.stdout.write(self.style.SUCCESS("Sare test mails bhej diye gaye hain!"))
