from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrMobileBackend(ModelBackend):
    """
    Custom authentication backend.
    Users can login using email or mobile along with password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = User.objects.get(Q(email__iexact=username) | Q(mobile=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
