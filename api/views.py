from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet

from .models import Books, Author, Category, Cart
from rest_framework.reverse import reverse
from .serializers import (
    BooksCreateSerializers,
    BooksReadSerializers,
    CategoryCreateSerializers,
    CategoryReadSeralizers,
    AuthorReadSerailizers,
    AuthorCreateSerializers,
    UserSerializer,
    CartSerializer,
    CartCreateSerializer,
)

# Create your views here.


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
    serializer_class = BooksCreateSerializers

    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return BooksCreateSerializers
    #     return BooksReadSerializers


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializers


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializers
    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return CategorySerializers
    #     return CategoryCreateSeralizers


class cartview(viewsets.ModelViewSet):
    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartCreateSerializer
        return CartSerializer


class userview(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]
