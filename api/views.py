from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import PermissionDenied

User = get_user_model()
from .models import Books, Author, Category, Cart, CartItem, CustomUser
from rest_framework.reverse import reverse
from .serializers import (
    BooksCreateSerializer,
    AuthorCreateSerializer,
    CategoryCreateSerializer,
    CartItemSerializer,
    CartSerializer,
    UserSerializer,
)

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .permissions import (
    IsAdminOrAuthorOrReadOnly,
    IsAdminOrAuthorSpecificOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminOrBuyerOnly,
    IsAdminOrAuthorOnly,
)


class BooksView(viewsets.ModelViewSet):
    """BookView Only Admin and Author can Crud Thier Books"""

    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "author":
            if not user.author_profile.is_verified:
                raise PermissionDenied(
                    "You are not verified. Verified authors only can create books."
                )
            serializer.save(author=user.author_profile, availability="pending")
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        book = self.get_object()
        if user.role == "author":
            if not user.author_profile.is_verified:
                raise PermissionDenied(
                    "You are not verified. Verified authors only can update books."
                )
            serializer.save(
                author=user.author_profile,
                availability=book.availability,
            )
        else:
            serializer.save()

    # def get_object(self
    #     obj = super().get_object()
    #     print(obj)
    #     if obj.author != self.request.user:
    #         raise PermissionDenied("You cannot access this book")
    #     return obj


class AuthorView(viewsets.ModelViewSet):
    """AuthorView Only Admin and Author can Crud Thier Own profile"""

    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorSpecificOrReadOnly]

    def perform_create(self, serializer):
        users = self.request.user

        if users.role == "author":
            serializer.save(is_verified=False, user=users)
        else:
            serializer.save()

    def perform_update(self, serializer):
        users = self.request.user
        author_db = self.get_object()

        if users.role == "author":
            serializer.save(is_verified=author_db.is_verified, user=users)
            print(users, author_db)
        else:
            serializer.save()


class AuthorSelfView(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorOnly]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Author.objects.none()

        if user.is_superuser or user.role == "admin":
            return Author.objects.all()

        if user.role == "author":
            return Author.objects.filter(user=user)

        return Author.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "author":
            serializer.save(user=user, is_verified=False)
        else:

            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        author_obj = self.get_object()

        if user.role == "author":
            serializer.save(user=author_obj.user, is_verified=author_obj.is_verified)
        else:

            serializer.save()


class CategoryView(viewsets.ModelViewSet):
    """CategoryView Only Admin and  can Crud Category"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CategoryFilter


class CartItemView(viewsets.ModelViewSet):
    """CartItmeView Only Admin and Buyer can Crud Thier Own CartItem"""

    serializer_class = CartItemSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return CartItem.objects.all()
        return CartItem.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser and user.role == "author":
            raise PermissionDenied("only buyer have permission to perform cartitem")

        if not user.is_superuser and user.role == "basic_user":
            serializer.save(user=user)
            return

        if user.is_superuser and user.role == "admin":
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        if user.role == "author" and not user.is_superuser:
            raise PermissionDenied("Authors cannot update cart items.")

        if user.role == "basic_user" and not user.is_superuser:
            if instance.user != user:
                raise PermissionDenied("You cannot update another user's cart.")
            serializer.save(user=user)
            return

        serializer.save()


class CartView(viewsets.ModelViewSet):
    """CartView Only Admin and Buyer can Crud Thier Own Cart"""

    serializer_class = CartSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == "admin":
            return Cart.objects.all()
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser and user.role == "author":
            raise PermissionDenied("only buyer have permission to perform cartitem")

        if not user.is_superuser and user.role == "basic_user":
            if hasattr(user, "cart"):
                raise PermissionDenied("You already have a cart.")
            serializer.save(user=user)
            return

        if user.is_superuser and user.role == "admin":
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        if user.role == "author" and not user.is_superuser:
            raise PermissionDenied("Authors cannot update cart items.")

        if user.role == "basic_user" and not user.is_superuser:
            if instance.user != user:
                raise PermissionDenied("You cannot update another user's cart.")
            serializer.save(user=user)
            return

        serializer.save()


class UserView(viewsets.ModelViewSet):
    """UserView Only Admin and User can Crud Thier Own CartItem"""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAdminOrAuthorOrBuyerOnly]

    def perform_create(self, serializer):
        user = self.request.user

        # ❌ Non-admin cannot create users
        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        # Non-admin users can update ONLY themselves
        if not user.is_superuser and user.role != CustomUser.ADMIN:
            if instance.id != user.id:
                raise PermissionDenied("You can update only your own profile.")

            serializer.save(role=instance.role)  # role locked
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user

        if self.request.method == "POST":
            return CustomUser.objects.none()

        if not user.is_authenticated:
            return CustomUser.objects.none()

        if user.is_superuser or user.role == CustomUser.ADMIN:
            return CustomUser.objects.all()

        return CustomUser.objects.filter(id=user.id)


@api_view(["GET"])
def home(request):

    info = {
        "rootendpint": "home/api/",
        "status": "home/status/",
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
            "author-filter": "api/books/?author=<author>",
            "category-filter": "api/books/?category=<category_name>",
        },
        "Author": {
            "total_authors": Author.objects.all().count(),
            "author": "api/author/",
            "author-details": "api/author/id",
            "author-filter": "api/author/?author=<author>",
            "category-filter": "api/author/?category=<category_name>",
        },
        "Category": {
            "category": "api/category/",
            "total_category": Category.objects.all().count(),
            "category-details": "api/category/id",
            "author-filter": "api/category/?author=<author",
            "category-filter": "api/category/?category=<category_name>",
        },
        "Stats": {"status": "home/staus/"},
        "Apiendpoint": {"status": "home/api/"},
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
        stats["books_by_author"][author.user.username] = author.books_of_author.count()
    # books by availability
    for choice in Books.AVAILABILITY_CHOICES:
        status_key = choice[0]
        status_label = choice[1]
        counts = Books.objects.filter(availability=status_key).count()
        stats["books_by_availability"][status_label] = counts
    return Response(stats)


#  faltu hai abhi k liye :


# def get_queryset(self):
#     user = self.request.user

#     if not user.is_authenticated:
#         return CustomUser.objects.none()

#     if user.role == "admin" or user.is_superuser:
#         return CustomUser.objects.all()
#
#     return CustomUser.objects.filter(id=user.id)
# http_method_names = ["get", "retrive", "update" "delete"]  # for specific


# def perform_create(self, serializer):
#     serializer.save(user=self.request.user)

# def perform_update(self, serializer):
#     serializer.save(user=self.request.user)


# def perform_update(self, serializer):
#         # User sirf apna data update kar sakta hai
#         serializer.save(id=self.request.user.id)

# def perform_destroy(self, instance):
#         # User sirf apna record delete kar sakta hai
#         if instance.id != self.request.user.id:
#             raise PermissionDenied("You don't have permission to delete this user.")
#         instance.delete()


# def dispatch(self, request, *args, **kwargs):
#    from django.utils import timezone


# user = self.request.user
#        print(
#            {
#                "path": request.path,
#                "method": request.method,
#                "user": str(user),
#                "ip": request.META.get("REMOTE_ADDR"),
#                "timestamp": timezone.now().isoformat(),
#            }
#        )
#
#        return super().dispatch(request, *args, **kwargs)
#
#    def get(self, request):
#        return Response({"msg": "GET Called"})
#

"""
# List all Types method and Hooks

| Operation | Method / Hook                | Purpose                                      |
| --------- | ---------------------------- | -------------------------------------------- |
| List      | `list()`                     | GET request handle, response prepare        |
| Create    | `create()`                   | POST request handle, response prepare        |
| Create    | `perform_create(serializer)` | Actual DB save, attach extra fields          |
| Retrieve  | `retrieve()`                 | GET single object handle, response prepare   |
| Retrieve  | `get_object()`               | Fetch object + object-level permission check |
| Update    | `update()`                   | PUT/PATCH request handle, response prepare   |
| Update    | `perform_update(serializer)` | Actual DB update + extra fields              |
| Delete    | `destroy()`                  | DELETE request handle, response prepare      |
| Delete    | `perform_destroy(instance)`  | Actual DB delete + logging                   |

| Hook                        | Purpose                                      |
| --------------------------- | -------------------------------------------- |
| `get_serializer_class()`    | Dynamic serializer selection based on action |
| `get_serializer()`          | Serializer instance create                   |
| `get_serializer_context()`  | Extra context pass to serializer             |
| `get_queryset()`            | Base queryset define                         |
| `filter_queryset(queryset)` | Queryset filter/search/order apply           |

| Hook                                     | Purpose                                 |
| ---------------------------------------- | --------------------------------------- |
| `initial(request, *args, **kwargs)`      | Pre-processing, auth & permission check |
| `get_permissions()`                      | Dynamic permission classes              |
| `get_authenticators()`                   | Dynamic authentication classes          |
| `check_object_permissions(request, obj)` | Object-level permission check           |
| `get_throttles()`                        | Throttling setup                        |
| `perform_authentication(request)`        | Explicit authentication run             |
| `check_throttles(request)`               | Explicit throttle check                 |

| Hook                                                    | Purpose                              |
| ------------------------------------------------------- | ------------------------------------ |
| `finalize_response(request, response, *args, **kwargs)` | Modify response before sending       |
| `handle_exception(exc)`                                 | Exception handling + custom response |

| Hook                           | Purpose                        |
| ------------------------------ | ------------------------------ |
| `paginate_queryset(queryset)`  | Apply pagination               |
| `get_paginated_response(data)` | Return paginated response      |
| `get_filter_backends()`        | Decide dynamic filter backends |
| `get_view_name()`              | Dynamic view name (for schema) |
| `get_view_description()`       | View description (for schema)  |
| `get_schema(request=None)`     | OpenAPI / Schema generation    |
| `get_renderer_context()`       | Extra rendering context        |


| Hook                                           | Purpose                             |
| ---------------------------------------------- | ----------------------------------- |
| `dispatch(request, *args, **kwargs)`           | Start of request lifecycle          |
| `initialize_request(request, *args, **kwargs)` | Convert HTTP request to DRF Request |
| `options(request, *args, **kwargs)`            | Handle HTTP OPTIONS request         |

"""
