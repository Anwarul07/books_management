from django.contrib import admin
from django.urls import path, include
from .views import (
    home,
    booksview,
    authorview,
    categoryview,
    CartItemView,
    cartview,
    RegisterView,
    SigninView,
)
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()


router.register("books", views.booksview, basename="books")
router.register("author", views.authorview, basename="author")
router.register("category", views.categoryview, basename="category")
router.register("cartitem", views.CartItemView, basename="cartitem")
router.register("cart", views.cartview, basename="cart")
# router.register("signin", views.SigninView, basename="customuser")


urlpatterns = [
    path("signup/", views.RegisterView.as_view(), name="customuser-list"),
    path(
        "signin/",
        views.SigninView.as_view({"get": "list"}),
        name="customuser-detail",
    ),
    path(
        "signin/<int:pk>/",
        views.SigninView.as_view(
            {"get": "retrieve", "delete": "destroy", "put": "update"}
        ),
        name="customuser-detail",
    ),
    path("", include(router.urls)),
    # path("", home, name="home"),
]


if settings.DEBUG:  # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
