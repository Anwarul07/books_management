from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from .models import Books, Author, Category
from rest_framework.reverse import reverse
from .serializers import BooksSerializers, AuthorSerializers, CategorySerializers

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
    serializer_class = BooksSerializers


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializers


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializers
