from django.contrib import admin
from django.urls import path, include
from .views import (
    home,
    BooksView,
    AuthorView,
    AuthorSelfView,
    CategoryView,
    CartItemView,
    CartView,
    UserView,
    SendOTPView,
    VerifyOTPView,
)
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()


router.register("books", views.BooksView, basename="books")
router.register("author", views.AuthorView, basename="author")
router.register("authors/me", views.AuthorSelfView, basename="authoronly")
router.register("category", views.CategoryView, basename="category")
router.register("cartitem", views.CartItemView, basename="cartitem")
router.register("cart", views.CartView, basename="cart")
router.register("user/register", views.UserView, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    path("", home, name="home"),
    path("status/", home, name="status"),
    path("register/send-otp/", SendOTPView.as_view()),
    path("register/verify-otp/", VerifyOTPView.as_view()),
]


# if settings.DEBUG:  # Serve media files during development
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
