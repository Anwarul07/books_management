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
    SendPasswordUpdateOTPView,
    UpdatePasswordConfirmView,
    SendForgetPasswordOTPView,
    ForgetPasswordConfirmView,
    SendUserDeleteOTPView,
    DeleteUserConfirmView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("silk/", include("silk.urls", namespace="silk")),

    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("", home, name="home"),
    path("status/", stats, name="status"),
    path("register/sendotp/", SendOTPView.as_view(), name="sendotp"),
    path("register-user/", UserRegisterView.as_view(), name="register"),
    path("login/sendotp/", SendLoginOTPView.as_view(), name="login-send-otp"),
    path("login-user/", LoginView.as_view(), name="login"),
    path("logout-user/", LogoutView.as_view(), name="logout"),
    path("logoutall/", LogoutAllView.as_view(), name="logoutall"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("password-update/otp/", SendPasswordUpdateOTPView.as_view()),
    path("password-update/", UpdatePasswordConfirmView.as_view()),
    path("forget-password/otp/", SendForgetPasswordOTPView.as_view()),
    path("forget-password/", ForgetPasswordConfirmView.as_view()),
    path("delete-user/otp/", SendUserDeleteOTPView.as_view()),
    path("delete-user/", DeleteUserConfirmView.as_view()),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
