from .otp import *
from api.filters import BooksFilter, CategoryFilter
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets, permissions
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated


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
    SendOTPSerializer,
    VerifyOTPAndRegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    LogoutAllSerializer,
    SendLoginOTPSerializer,
    SendPasswordUpdateOTPSerializer,
    VerifyOTPAndUpdatePasswordSerializer,
    VerifyOTPAndResetPasswordSerializer,
    SendForgetPasswordOTPSerializer,
    SendUserDeleteOTPSerializer,
    VerifyOTPAndDeleteUserSerializer,
)
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)
from rest_framework.authentication import SessionAuthentication
from .permissions import (
    IsAdminOrAuthorOrReadOnly,
    IsAdminOrAuthorSpecificOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminOrBuyerOnly,
    IsAdminOrAuthorOnly,
    IsAdminOrAuthorOrBuyerOnly,
    IsAdminOrAnonymousOnly,
)


class BooksView(viewsets.ModelViewSet):
    """BookView Only Admin and Author can Crud Thier Books"""

    queryset = Books.objects.all()
    serializer_class = BooksCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BooksFilter
    search_fields = ["title", "category__category_name"]
    ordering_fields = ["price", "publication_date", "title"]

    def get_queryset(self):
        queryset = Books.objects.select_related(
            "author", "author__user", "category"
        ).all()  # Search
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(isbn__icontains=search)
                | Q(author__user__username__icontains=search)
                | Q(author__user__first_name__icontains=search)
                | Q(author__user__last_name__icontains=search)
            )
            # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(
                category__category_name__iexact=category
            )  # Filter by availability
        availability = self.request.query_params.get("availability")
        if availability is not None:
            queryset = queryset.filter(availability=availability)  # Filter by author
        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(
                Q(author__user__username__icontains=author)
                | Q(author__user__first_name__icontains=author)
                | Q(author__user__last_name__icontains=author)
            )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "author":
            if not user.author_profile.is_verified:
                raise PermissionDenied(
                    "You are not verified. Verified authors only can create books."
                )
            serializer.save(
                author=user.author_profile,
                availability="pending",
            )
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


class AuthorView(viewsets.ModelViewSet):
    """AuthorView Only Admin and Author can Crud Thier Own profile"""

    queryset = Author.objects.all()
    serializer_class = AuthorCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAuthorSpecificOrReadOnly]

    def perform_create(self, serializer):
        users = self.request.user

        if users.is_authenticated and not users.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        if users.role == "author":
            serializer.save(is_verified=False, user=users)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        author = self.get_object()

        # AUTHOR cannot self-verify
        if user.role == "author":
            serializer.save(is_verified=author.is_verified)
            return

        # ADMIN can verify / reject
        if user.is_superuser or user.role == "admin":
            serializer.save()  # 🔥 Author.save() → signal fires
            return

        raise PermissionDenied("You are not allowed to update this profile.")


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

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        if user.role == "author":
            serializer.save(user=user, is_verified=False)
        else:

            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        author = self.get_object()

        # AUTHOR cannot self-verify
        if user.role == "author":
            serializer.save(is_verified=author.is_verified)
            return

        # ADMIN can verify / reject
        if user.is_superuser or user.role == "admin":
            serializer.save()  # 🔥 Author.save() → signal fires
            return

        raise PermissionDenied("You are not allowed to update this profile.")

    # def get_object(self):
    #     obj = super().get_object()
    #     print(obj)
    #     if obj.id != self.request.user.id:
    #         raise PermissionDenied("You cannot access this book")
    #     return obj


class CategoryView(viewsets.ModelViewSet):
    """CategoryView Only Admin and  can Crud Category"""

    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    permission_classes = [IsAdminOrReadOnly]

    # filter_backends = [DjangoFilterBackend]
    # filterset_class = CategoryFilter


class CartItemView(viewsets.ModelViewSet):
    """CartItmeView Only Admin and Buyer can Crud Thier Own CartItem"""

    qeuryset = CartItem.objects.all()
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

    def get_object(self):
        obj = super().get_object()
        print(obj.user, self.request.user)
        if obj.id != self.request.user.id:
            raise PermissionDenied("You cannot access this book")
        return obj


class CartView(viewsets.ModelViewSet):
    """CartView Only Admin and Buyer can Crud Thier Own Cart"""

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrBuyerOnly]

    def get(self, request, *args, **kwargs):
        print("AUTH:", request.auth)
        print("USER:", request.user)

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
    permission_classes = [IsAdminOrAuthorOrBuyerOnly]

    def get_serializer_class(self):
        request = self.request
        user = request.user
        if self.request.method == "POST":
            if self.request.user.is_authenticated and self.request.user.is_superuser:
                return UserSerializer
            return VerifyOTPAndRegisterSerializer

        if self.request.method in ["PUT", "PATCH"]:
            # Admin → direct serializer
            if user.is_superuser or user.role == CustomUser.ADMIN:
                return UserSerializer

            # Non-admin password update → OTP serializer
            if "password" in request.data:
                return VerifyOTPAndUpdatePasswordSerializer

            # Non-admin profile update
            return UserSerializer

        return UserSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # ❌ Non-admin logged in  cannot create another  users
        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        target = self.get_object()

        if user.is_superuser or user.role == "admin":
            serializer.save()
            return

        #  ---------- AUTHOR / BASIC USER (SELF ONLY) ----------
        if user.id == target.id:
            serializer.save(
                role=target.role,
                is_superuser=target.is_superuser,
                is_staff=target.is_staff,
            )
            return

        raise PermissionDenied("You are not allowed to update this user.")

    def get_queryset(self):
        user = self.request.user

        if self.request.method == "POST":
            return CustomUser.objects.none()

        if not user.is_authenticated:
            return CustomUser.objects.none()

        if user.is_superuser or user.role == CustomUser.ADMIN:
            return CustomUser.objects.all()

        return CustomUser.objects.filter(id=user.id)


# OTP Views


class SendOTPView(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = SendOTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAnonymousOnly]

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_via = serializer.validated_data.get("otp_via")
        email = serializer.validated_data.get("email")
        mobile = serializer.validated_data.get("mobile")

        otp_obj = serializer.save()
        return Response(
            {
                "message": "OTP sent successfully via {}".format(otp_via),
                "email": otp_obj.email,
                "mobile": otp_obj.mobile,
                "send_time": otp_obj.created_at,
                "expires_at": otp_obj.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class UserRegisterView(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = VerifyOTPAndRegisterSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminOrAnonymousOnly]

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            raise PermissionDenied(
                "You are already logged in. You cannot register another user."
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_user = serializer.save()
        return Response(
            {
                "message": "User registered successfully",
                "user_id": created_user.id,
                "email": created_user.email,
                "mobile": created_user.mobile,
                "role": created_user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class SendLoginOTPView(generics.CreateAPIView):
    """
    Send OTP for login via Email or Mobile
    """

    serializer_class = SendLoginOTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "otp_via": otp.otp_via,
                "message": f"OTP sent successfully for {otp.otp_via} login.",
                "email": otp.email,
                "mobile": otp.mobile,
                "expires_at": otp.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(generics.CreateAPIView):
    serializer_class = LogoutSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class LogoutAllView(generics.CreateAPIView):
    serializer_class = LogoutAllSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Logged out from all devices"}, status=status.HTTP_200_OK
        )


class SendPasswordUpdateOTPView(generics.CreateAPIView):
    serializer_class = SendPasswordUpdateOTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent successfully for password update",
                "expires_at": otp.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class UpdatePasswordConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndUpdatePasswordSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Password updated successfully. Please login again.",
                "relogin_required": True,
            },
            status=status.HTTP_200_OK,
        )


class SendForgetPasswordOTPView(generics.CreateAPIView):
    serializer_class = SendForgetPasswordOTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent for password reset",
                "expires_at": otp.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class ForgetPasswordConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndResetPasswordSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Password reset successful. Please login again.",
                "relogin_required": True,
            },
            status=status.HTTP_200_OK,
        )


class SendUserDeleteOTPView(generics.CreateAPIView):
    serializer_class = SendUserDeleteOTPSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()

        return Response(
            {
                "message": "OTP sent for account deletion",
                "expires_at": otp.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class DeleteUserConfirmView(generics.CreateAPIView):
    serializer_class = VerifyOTPAndDeleteUserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Account deleted successfully",
                "relogin_required": True,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def home(request):

    info = {
        "rootendpint": "home/api/",
        "status": "home/status/",
        "Books": {
            "books": "/api/books/",
            # "books": reverse("books", request=request, format=format),
            "total_pending_books": Books.objects.filter(
                availability__iexact="pending"
            ).count(),
            "total_available_books": Books.objects.filter(
                availability__iexact="available"
            ).count(),
            "books": "/api/books/",
            "books-details": "/api/books/id",
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
        "Stats": {"status": "/staus/"},
        "Apiendpoint": {"apiroot": "/api/"},
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
