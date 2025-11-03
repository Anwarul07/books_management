from django.contrib import admin
from django.urls import path, include
from .views import home, booksview, cartview, userview, cartlistview
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()

router.register("books", views.booksview, basename="books")
router.register("author", views.authorview, basename="author")
router.register("category", views.categoryview, basename="category")
router.register("cart", views.cartview, basename="cart")
router.register("cartlist", views.cartlistview, basename="cartlist")
router.register("user", views.userview, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    # path("", home, name="home"),
]


if settings.DEBUG:  # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
