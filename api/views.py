from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Q
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

User = get_user_model()

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

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework import permissions
from .permissions import UserRolepermission, IsAdminOrAuthorOrReadOnly


class booksview(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer
    authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAdminOrAuthorOrReadOnly]


class authorview(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer


class categoryview(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CategoryFilter


class CartItemView(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class cartview(viewsets.ModelViewSet):
    queryset=Cart.objects.all()
    serializer_class = CartSerializer

    # def get_queryset(self):
    #     users = self.request.user

    #     if not users.is_authenticated or users.role == "author":
    #         return Cart.objects.none()
    #     if users.role == "admin" or users.is_superuser:
    #         return Cart.objects.all()
    #     return CustomUser.objects.filter(id=users.id)


class SigninView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [UserRolepermission]

    # def get_queryset(self):
    #     user = self.request.user

    #     if not user.is_authenticated:
    #         return CustomUser.objects.none()

    #     # Admin sab dekh sakta hai
    #     if user.role == "admin" or user.is_superuser:
    #         return CustomUser.objects.all()

    #     # Author/Basic User sirf apna data query kar payenge
    #     # (Ye double security hai permission class ke saath)
    #     return CustomUser.objects.filter(id=user.id)
    # http_method_names = ["get", "retrive", "update" "delete"]  # for specific


# from .permissions import RegisterPermission

from rest_framework.generics import CreateAPIView
from .permissions import RegisterPermission


class RegisterView(CreateAPIView):
    http_method_names = ["post"]  # for specific
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


# author
# def get_queryset(self):
#     author = self.request.author
#     return Author.objects.filter(author=author).order_by("-id")

# cart

# def get_queryset(self):
#     # Only return logged-in user's cart items
#     return CartItem.objects.filter(user=self.request.user)

# def perform_create(self, serializer):
#     serializer.save(user=self.request.user)

# def perform_update(self, serializer):
#     serializer.save(user=self.request.user)


# idk ----

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


# def get_queryset(self):
#     user = self.request.user

#     if user.is_authenticated and user.role == CustomUser.ADMIN:
#         return CustomUser.objects.all()
#     return CustomUser.objects.filter(id=user.id)

# def get_queryset(self):
#     user = self.request.user.username
#     return CustomUser.objects.filter(user=user)


#     def get_queryset(self):
#         # Logged-in user ka sirf apna record return karega
#         return CustomUser.objects.filter(id=self.request.user.id)

#     def perform_update(self, serializer):
#         # User sirf apna data update kar sakta hai
#         serializer.save(id=self.request.user.id)

#     def perform_destroy(self, instance):
#         # User sirf apna record delete kar sakta hai
#         if instance.id != self.request.user.id:
#             raise PermissionDenied("You don't have permission to delete this user.")
#         instance.delete()


#
