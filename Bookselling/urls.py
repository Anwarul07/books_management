from django.contrib import admin
from django.urls import path, include

# from api import views
from api.views import home, stats, SendOTPView, UserRegisterView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("", home, name="home"),
    path("status/", stats, name="status"),
    path("sendotp/", SendOTPView.as_view(), name="sendotp"),
    path("register/", UserRegisterView.as_view(), name="register"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
