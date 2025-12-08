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
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import (
    IsAdminOrAuthorOrReadOnly,
    IsAdminOrAuthorSpecificOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminOrBuyerOnly,
    IsAdminOrAuthorOrBuyerOnly,
)


class booksview(viewsets.ModelViewSet):
    """BookView Only Admin and Author can Crud Thier Books"""

    # Need Hooks like perform create and Update etc user attach

    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    from rest_framework.response import Response

    def dispatch(self, request, *args, **kwargs):
        from django.utils import timezone

        user = self.request.user
        print(
            {
                "path": request.path,
                "method": request.method,
                "user": str(user),
                "ip": request.META.get("REMOTE_ADDR"),
                "timestamp": timezone.now().isoformat(),
            }
        )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return Response({"msg": "GET Called"})

    # def get_object(self):
    #     obj = super().get_object()  # default object fetch
    #     if not self.request.user.is_staff and obj.owner != self.request.user:
    #         raise PermissionDenied("You cannot access this book")
    #     return obj


class authorview(viewsets.ModelViewSet):
    """AuthorView Only Admin and Author can Crud Thier Own profile"""

    # Need Hooks like perform update

    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorSpecificOrReadOnly]


class categoryview(viewsets.ModelViewSet):
    """CategoryView Only Admin and  can Crud Category"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CategoryFilter


class CartItemView(viewsets.ModelViewSet):
    """CartItmeView Only Admin and Buyer can Crud Thier Own CartItem"""

    # Need perform Hooks and permission issuu to see all users at has permission need queeryset also  cart
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]


class cartview(viewsets.ModelViewSet):
    """CartView Only Admin and Buyer can Crud Thier Own Cart"""

    # Need perform Hooks and permission issuu to see all users at has permission need queeryset also  cart

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]


class userview(viewsets.ModelViewSet):
    """UserView Only Admin and User can Crud Thier Own CartItem"""

    # Need perform Hooks and permission issuu to see all users at has permission need queeryset also  user and only post sytem need

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorOrBuyerOnly]


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
