from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet

from .models import Books, Author, Category, Cart, Wishlist
from rest_framework.reverse import reverse
from .serializers import (
    BooksSerializers,
    BooksListSerializers,
    CategoryRead,
    AuthorRead,
    AuthorSerializers,
    CartSerializer,
    WishlistSerializer,
    CategorySerializers,
    CartCreateSerializer,
    WishCreateSeralizer,
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
    # serializer_class = BooksSerializers

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BooksSerializers
        return BooksListSerializers


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializers


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers
    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return CategorySerializers
    #     return CategoryRead


class cartview(viewsets.ModelViewSet):
    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CartCreateSerializer
        return CartSerializer


class wishlistview(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WishCreateSeralizer
        return WishlistSerializer
