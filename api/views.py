from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Books, Author, Category, Cart, CartItem
from rest_framework.reverse import reverse
from .serializers import (
    BooksReadSerializer,
    BooksCreateSerializer,
    AuthorReadSerializer,
    AuthorCreateSerializer,
    CategoryReadSerializer,
    CategoryCreateSerializer,
    CartItemSerializer,
    CartSerializer,
    UserSerializer,
)


@api_view(["GET"])
def home(request, format=None):

    info = {
        "root": "api/",
        "books": "api/books/",
        "author": "api/author/",
        "category": "api/category/",
        # "books": reverse("books", request=request, format=format),
    }
    return Response(info)


class booksview(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer


class cartitemview(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class cartview(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class userview(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
