# managers.py

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied  # इसे import करें


class CustomUserManager(BaseUserManager):

    # 🔑 1. सामान्य User बनाने के लिए (कोई बदलाव नहीं)
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "basic_user")
        if not username:
            raise ValueError(_("The Username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 🔑 2. Superuser (Admin) बनाने के लिए (सुधार किया गया)
    def create_superuser(self, username, email, password=None, **extra_fields):

        # 🎯 सुधारित Admin चेक: किसी भी Superuser के अस्तित्व की जाँच करें
        # यह सुनिश्चित करता है कि सिर्फ़ तभी check करें जब हम नया Superuser बना रहे हों।
        if self.filter(is_superuser=True).exists():
            # यदि पहला Superuser पहले से मौजूद है
            # और जो user अभी बनाने की कोशिश कर रहा है वह Superuser है (डिफ़ॉल्ट रूप से True)
            # तो इसे ब्लॉक कर दें।
            if extra_fields.get("is_superuser", True) is True:
                # PermissionError की जगह Django की PermissionDenied का उपयोग करें
                raise PermissionDenied(
                    "A Superuser/Admin already exists in this system. Only one is allowed."
                )

        # Admin User को अनिवार्य flags और 'admin' role सेट करें
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, email, password, **extra_fields)
