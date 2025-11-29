from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrMobileBackend(ModelBackend):
    """
    Custom authentication backend.
    Users can login using email or mobile along with password.
    Username is ignored.
    Only active users can login.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email or mobile and password.
        """
        if not username or not password:
            return None

        # Normalize input
        username_input = username.strip()
        mobile_input = username_input.replace(" ", "").replace("-", "")

        try:
            user = User.objects.get(
                Q(email__iexact=username_input) | Q(mobile=mobile_input)
            )
        except User.DoesNotExist:
            return None

        # Only active users
        if user.check_password(password) and user.is_active:
            return user

        return None
