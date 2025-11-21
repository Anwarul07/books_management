from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

User = get_user_model()
from .filters import BooksFilter, CategoryFilter

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


class booksview(viewsets.ModelViewSet):
    serializer_class = BooksCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = BooksFilter
    filterset_fields = [
        "title",
        "price",
        "language",
        "availablity",
        "binding_types",
        "edition",
        "ratings",
        "isbn",
    ]
    search_fields = [
        "=title",
        "category__category_name",
        "author__author_name",
        "binding_types",
        "language",
        "price",
    ]
    ordering_fields = ["title", "price", "availablity", "category__category_name"]

    def get_queryset(self):
        queryset = Books.objects.select_related("author", "category").filter(
            availablity__iexact="pending"
        )
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(author__author_name__icontains=search)
                | Q(category__category_name__icontains=search)
                | Q(publications__icontains=search)
                | Q(language__icontains=search)
                | Q(availablity__icontains=search)
                | Q(binding_types__icontains=search)
                | Q(edition__icontains=search)
            )
        # Filter on the basis on category
        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(category__category_name__iexact=category)

        # Filter on the base of Author
        author = self.request.query_params.get("author", None)
        if author:
            queryset = queryset.filter(author__author_name__iexact=author)

        return queryset


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer

    # def get_queryset(self):
    #     author = self.request.author
    #     return Author.objects.filter(author=author).order_by("-id")


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


class cartitemview(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class cartview(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class userview(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["GET"])
def home(request):

    info = {
        "root": "api/",
        "Books": {
            "books": "api/books/",
            # "books": reverse("books", request=request, format=format),
            "total_pending_books": Books.objects.filter(
                availablity__iexact="pending"
            ).count(),
            "total_available_books": Books.objects.filter(
                availablity__iexact="available"
            ).count(),
            "books": "api/books/",
            "books-details": "api/books/id",
            "total_books": Books.objects.all().count(),
            "author-filter": "api/books/?author=<author_name>",
            "category-filter": "api/books/?category=<category_name>",
        },
        "Author": {
            "total_authors": Author.objects.all().count(),
            "author": "api/author/",
            "author-details": "api/author/id",
            "author-filter": "api/author/?author=<author_name>",
            "category-filter": "api/author/?category=<category_name>",
        },
        "Category": {
            "category": "api/category/",
            "total_category": Category.objects.all().count(),
            "category-details": "api/category/id",
            "author-filter": "api/category/?author=<author_name>",
            "category-filter": "api/category/?category=<category_name>",
        },
        "Stats": {"status": "api/staus/"},
    }
    return Response(info)


@api_view(["GET"])
def stats(request):
    stats = {
        "total_books": Books.objects.count(),
        "available_books": Books.objects.filter(availablity="available").count(),
        "borrowed_books": Books.objects.filter(availablity="borrowed").count(),
        "total_authors": Author.objects.count(),
        "total_categories": Category.objects.count(),
        "books_by_category": {},
        "books_by_author": {},
        "books_by_availability": {},
    }

    # books by category
    for category in Category.objects.all():
        stats["books_by_category"][
            category.category_name
        ] = category.category_of_books.count()

    # books by author
    for author in Author.objects.all():
        stats["books_by_author"][author.author_name] = author.books_of_author.count()
    # books by availability
    for choice in Books.AVAILABILITY_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(availablity=status_key).count()
        stats["books_by_availability"][status_label] = counts
    return Response(stats)
