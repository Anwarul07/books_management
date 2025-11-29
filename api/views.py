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
# from .filters import BooksFilter, CategoryFilter

from .models import Books, Author, Category, Cart, CartItem, CustomUser
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
    queryset = Books.objects.prefetch_related("author", "category").all()
    serializer_class = BooksCreateSerializer
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAdminUser]

    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = BooksFilter
    # filterset_fields = [
    #     "title",
    #     "price",
    #     "language",
    #     "availability",
    #     "binding_types",
    #     "edition",
    #     "ratings",
    #     "isbn",
    # ]
    # search_fields = [
    #     "=title",
    #     "category__category_name",
    #     "author__author_name",
    #     "binding_types",
    #     "language",
    #     "price",
    # ]
    # ordering_fields = ["title", "price", "availability", "category__category_name"]

    # def get_queryset(self):
    #     queryset = Books.objects.select_related("author", "category").filter(
    #         availability__iexact="pending"
    #     )
    #     search = self.request.query_params.get("search", None)
    #     if search:
    #         queryset = queryset.filter(
    #             Q(title__icontains=search)
    #             | Q(author__user__username__icontains=search)
    #             | Q(author__user__first_name__icontains=search)
    #             | Q(author__user__last_name__icontains=search)
    #             | Q(category__category_name__icontains=search)
    #             | Q(publications__icontains=search)
    #             | Q(language__icontains=search)
    #             | Q(availability__icontains=search)
    #             | Q(binding_types__icontains=search)
    #             | Q(edition__icontains=search)
    #         )
    #     # Filter on the basis on category
    #     category = self.request.query_params.get("category", None)
    #     if category:
    #         queryset = queryset.filter(category__category_name__iexact=category)

    #     # Filter on the base of Author
    #     author = self.request.query_params.get("author", None)
    #     if author:
    #         queryset = queryset.filter(author__user__username__iexact=author)

    #     return queryset


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
    # filterset_class = CategoryFilter


class CartItemView(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    # def get_queryset(self):
    #     # Only return logged-in user's cart items
    #     return CartItem.objects.filter(user=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    # def perform_update(self, serializer):
    #     serializer.save(user=self.request.user)


class cartview(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class userview(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


@api_view(["GET"])
def home(request):

    info = {
        "root": "api/",
        "Books": {
            "books": "api/books/",
            # "books": reverse("books", request=request, format=format),
            "total_pending_books": Books.objects.filter(
                availability__iexact="pending"
            ).count(),
            "total_available_books": Books.objects.filter(
                availability__iexact="available"
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
        "available_books": Books.objects.filter(availability="available").count(),
        "borrowed_books": Books.objects.filter(availability="borrowed").count(),
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
        counts = Books.objects.filter(availability=status_key).count()
        stats["books_by_availability"][status_label] = counts
    return Response(stats)


# from rest_framework import viewsets
# from .models import CustomUser
# from rest_framework.permissions import IsAuthenticated
# from .serializers import UserSerializer
# from .permissions import IsAdminOrSelf  # Nayi permission class import karein


# class UserViewSet(viewsets.ModelViewSet):  # UserViewSet naming convention better hai
#     queryset = CustomUser.objects.all()  # CustomUser import karna zaruri hai
#     serializer_class = UserSerializer

#     # Permission yahan set karein
#     permission_classes = [IsAdminOrSelf]

#     # Optional: Agar koi user sirf apni profile dekhna chahe to
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated and user.role != CustomUser.ADMIN:
#             # Non-admin users sirf apni profile dekh sakte hain
#             return CustomUser.objects.filter(pk=user.pk)
#         return CustomUser.objects.all()
