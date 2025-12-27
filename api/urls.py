from django.contrib import admin
from django.urls import path, include
from .views import (
    home,
    stats,
    BooksView,
    AuthorView,
    AuthorSelfView,
    CategoryView,
    CartItemView,
    CartView,
    # UserView,
    SendOTPView,
    UserRegisterView,
)
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()


router.register("books", views.BooksView, basename="books")
router.register("authors", views.AuthorView, basename="author")
router.register("author/profile", views.AuthorSelfView, basename="authoronly")
router.register("category", views.CategoryView, basename="category")
router.register("cartitem", views.CartItemView, basename="cartitem")
router.register("mycarts", views.CartView, basename="cart")
router.register("users", views.UserView, basename="user")


urlpatterns = [
    path("", include(router.urls)),

]


if settings.DEBUG:  # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
