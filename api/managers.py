from django.contrib.auth.base_user import BaseUserManager

# from .models import CustomUser


class CustomUserManager(BaseUserManager):

    def create_user(
        self, username, email, mobile, password=None, role=None, **extra_fields
    ):
        """
        Create normal user with specified role.
        Role must be one of CustomUser.ROLE_CHOICES
        """
        if not username:
            raise ValueError(_("The Username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        if not mobile:
            raise ValueError(_("The Mobile number must be set"))

        # role_choices = [choice[0] for choice in CustomUser.ROLE_CHOICES]
        # if role not in role_choices:
        #     raise ValueError(_(f"Role must be one of {role_choices}"))

        email = self.normalize_email(email)
        user = self.model(
            username=username, email=email, mobile=mobile, role=role, **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, mobile, password=None, **extra_fields):
        """
        Superuser always has admin role
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # extra_fields.setdefault("role", CustomUser.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(
            username=username,
            email=email,
            mobile=mobile,
            password=password,
            # role=CustomUser.ADMIN,
            **extra_fields,
        )
