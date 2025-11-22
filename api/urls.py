from django.contrib import admin
from django.urls import path, include
from .views import home, booksview, cartview, userview, cartitemview, stats
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()

router.register("books", views.booksview, basename="books")
router.register("author", views.authorview, basename="author")
router.register("category", views.categoryview, basename="category")
router.register("cartlist", views.cartitemview, basename="cartlist")
router.register("cart", views.cartview, basename="cart")
router.register("user", views.userview, basename="customuser")


urlpatterns = [
    path("", include(router.urls)),
    # path("", home, name="home"),
]


if settings.DEBUG:  # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
