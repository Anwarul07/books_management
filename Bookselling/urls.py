from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView


# from api import views
from api.views import (
    home,
    stats,
    SendOTPView,
    UserRegisterView,
    LoginView,
    LogoutView,
    LogoutAllView,
    SendLoginOTPView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", home, name="home"),
    path("status/", stats, name="status"),
    path("sendotp/", SendOTPView.as_view(), name="sendotp"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/sendotp/", SendLoginOTPView.as_view(), name="login-send-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logoutall/", LogoutAllView.as_view(), name="logoutall"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
