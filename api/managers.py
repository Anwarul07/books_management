# managers.py

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    # 🔑 1. सामान्य User बनाने के लिए
    def create_user(self, username, email, password=None, **extra_fields):
        # Default role सेट करें, जिसे models.py में बदला जा सकता है
        extra_fields.setdefault("role", "basic_user")

        if not username:
            raise ValueError(_("The Username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)

        # Password को Hash करें (सुरक्षा के लिए अनिवार्य)
        user.set_password(password)

        user.save(using=self._db)
        return user

    # 🔑 2. Superuser (Admin) बनाने के लिए
    def create_superuser(self, username, email, password=None, **extra_fields):
        # Admin User को अनिवार्य flags और 'admin' role सेट करें
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  # 🎯 Admin Role असाइन करें

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        # create_user method का उपयोग करके user बनाएँ
        return self.create_user(username, email, password, **extra_fields)
