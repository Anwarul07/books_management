from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from decimal import Decimal
from .models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.db import transaction
from .otp import *
from django.contrib.auth.hashers import make_password


from django.contrib.auth import get_user_model

User = get_user_model()

from .models import (
    Books,
    Author,
    Category,
    CartItem,
    Cart,
    OTP,
)


# ---------------- Books Read Serializer for assign only Book detail in any seralizers ----------------
class BooksReadSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale_price = serializers.ReadOnlyField()

    # Author assignment restricted to users with role "author"
    # author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    class Meta:
        model = Books
        fields = "__all__"

    def get_author_name(self, obj):

        author = obj.author
        try:
            return obj.author.author_profile.author_name
        except ObjectDoesNotExist:
            return f"User: {obj.author.username}"

        except Exception:
            return obj.author.user.username

            # return obj.author.first_name + " " + obj.author.last_name

    def validate_author(self, value):
        if value.user.role != CustomUser.AUTHOR:
            raise serializers.ValidationError(
                "The associated user must have the role 'author'."
            )
        return value


# ---------------- Author Read Serializer for assign only Author detail in any seralizers ----------------
class AuthorReadSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="id", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    author_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)

    cover_image = serializers.ImageField(source="user.cover_image", read_only=True)
    front_image = serializers.ImageField(source="user.front_image", read_only=True)
    behind_image = serializers.ImageField(source="user.behind_image", read_only=True)
    side_image = serializers.ImageField(source="user.side_image", read_only=True)
    top_image = serializers.ImageField(source="user.top_image", read_only=True)
    bottom_image = serializers.ImageField(source="user.bottom_image", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="author")
    )

    class Meta:
        model = Author
        fields = "__all__"

    def get_author_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def validate_user(self, value):
        if value.role != "author":
            raise serializers.ValidationError(
                "Only Author users can be assigned as book author."
            )
        return value


# ---------------- Category Read Serializer for assign only Category detail in any seralizers ----------------
class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# ---------------- Book Create Serializer for Book details----------------
class BooksCreateSerializer(serializers.ModelSerializer):
    author_details = AuthorReadSerializer(read_only=True, source="author")
    category_details = CategoryReadSerializer(read_only=True, source="category")

    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale_price = serializers.SerializerMethodField()
    # viewed_by = serializers.SerializerMethodField()

    # Author assignment restricted to users with role "author"
    # author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    class Meta:
        model = Books
        fields = "__all__"
        read_only_fields = [
            "author_name",
            "author_details",
            "category_name",
            "category_details",
            "sale_price",
            "created_at",
            "updated_at",
            # "viewed_by",
        ]

    def get_author_name(self, obj):
        return f"{obj.author.user.first_name} {obj.author.user.last_name}"

    def get_sale_price(self, obj):
        discount_percentage = Decimal(obj.discount or 0) / Decimal(100)
        total = obj.price * (Decimal(1) - discount_percentage)
        return round(total, 2)

    def validate_author(self, value):
        request = self.context.get("request")
        user = request.user

        if value.user.role != CustomUser.AUTHOR:
            raise serializers.ValidationError(
                "The associated user must have the role 'author'."
            )

        if user.role == "author" and value != user.author_profile:
            raise serializers.ValidationError(
                "Authors cannot change or assign the author field. Only admin can do this."
            )
        return value

    def validate_availability(self, value):
        request = self.context.get("request")
        user = request.user

        if not hasattr(user, "author_profile"):
            return value

        instance = getattr(self, "instance", None)
        if instance is None:
            if "availability" not in request.data:
                raise serializers.ValidationError(
                    "Authors cannot modify availability. Admin approval required."
                )
            return "pending"

        old_value = instance.availability
        if value != old_value:
            raise serializers.ValidationError(
                "Authors cannot modify availability. Admin approval required."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        # Author but not verified → block
        if user.role == "author" and not user.author_profile.is_verified:
            raise serializers.ValidationError(
                "Only verified authors can create or update books."
            )

        return attrs

    # def get_viewed_by(self, obj):
    #     user = self.context["request"].user
    #     return user.username

    # def get_fields(self):
    #     fields = super().get_fields()
    #     user = self.context["request"].user
    #     if not user.is_superuser:
    #         fields.pop("availability")  # hide sensitive field
    #     return fields


# ---------------- Author Create Serializer for Author details----------------
class AuthorCreateSerializer(serializers.ModelSerializer):
    # User related fields
    user_id = serializers.CharField(source="user.id", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True)

    cover_image = serializers.ImageField(source="user.cover_image", read_only=True)
    front_image = serializers.ImageField(source="user.front_image", read_only=True)
    behind_image = serializers.ImageField(source="user.behind_image", read_only=True)
    side_image = serializers.ImageField(source="user.side_image", read_only=True)
    top_image = serializers.ImageField(source="user.top_image", read_only=True)
    bottom_image = serializers.ImageField(source="user.bottom_image", read_only=True)

    # Books reverse relation -> from Books model: author = FK(CustomUser)
    books_of_author = BooksReadSerializer(
        source="user.books", many=True, read_only=True
    )

    # Aggregates
    totalbooks = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    category_of_books = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="author")
    )

    class Meta:
        model = Author
        fields = "__all__"

        read_only_fields = [
            "username",
            "email",
            "mobile",
            "books_of_author",
            "totalbooks",
            "category_of_books",
            "totalcategory",
        ]

    def validate_user(self, value):
        request = self.context.get("request")
        user = request.user

        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if value.role != "author":
            raise serializers.ValidationError(
                "Only  Author users can be assigned as book author."
            )
        return value

    def validate_is_verified(self, value):
        request = self.context.get("request")
        if request is None:
            return value

        user = request.user
        instance = getattr(self, "instance", None)

        # ---------------- CREATE ----------------
        if instance is None:
            if user.role == "author":
                if "is_verified" in request.data:
                    raise serializers.ValidationError(
                        "Authors cannot update verification status. Admin approval required."
                    )
                return False
            return value

        # ---------------- UPDATE ----------------
        old_value = instance.is_verified
        if value != old_value and user.role != "admin":
            raise serializers.ValidationError(
                "Authors cannot update verification status. Admin approval required."
            )

        return value

    # Dynamically change user field (admin vs buyer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not request:
            return

        user = request.user

        if not user.is_authenticated:
            self.fields["user"].read_only = True
            return
        if not user.is_superuser and user.role != "admin":
            self.fields["user"].read_only = True
            self.fields["user"].default = serializers.CurrentUserDefault()

        else:
            self.fields["user"].queryset = CustomUser.objects.filter(role="author")

    # ------------------------ AGGREGATION ------------------------

    def get_totalbooks(self, obj):
        return obj.books_of_author.count()

    def get_totalcategory(self, obj):
        return obj.books_of_author.values_list("category", flat=True).distinct().count()

    def get_category_of_books(self, obj):
        categories = Category.objects.filter(category_of_books__author=obj).distinct()
        return CategoryReadSerializer(categories, many=True).data


# ---------------- Book Categoty Serializer for Category details----------------
class CategoryCreateSerializer(serializers.ModelSerializer):
    category_of_books = BooksReadSerializer(many=True, read_only=True)

    totalbook = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    totalauthors = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

        read_only_fields = [
            "category_of_books",
            "totalbook",
            "authors",
            "totalauthors",
            "created_at",
            "updated_at",
        ]

    def get_totalbook(self, obj):
        return obj.category_of_books.count()

    def get_authors(self, obj):
        data = authors_qs = (
            Author.objects.filter(books_of_author__category=obj)
            .distinct()
            .select_related("user")
        )
        unique_authors = [
            {
                "user_id": author.user.id,
                "first_name": author.user.first_name,
                "last_name": author.user.last_name,
                "email": author.user.email,
            }
            for author in data
        ]

        return unique_authors

    def get_totalauthors(self, obj):
        return obj.category_of_books.values_list("author", flat=True).distinct().count()


# ---------------- CartItem Create Serializer for CartItem details----------------
class CartItemSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    book_title = serializers.CharField(source="books.title", read_only=True)

    book_price = serializers.DecimalField(
        source="books.price", max_digits=10, decimal_places=2, read_only=True
    )
    book_discount = serializers.DecimalField(
        source="books.discount", max_digits=5, decimal_places=2, read_only=True
    )

    sale_price = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="basic_user")
    )

    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ("added_at", "updated_at")

    # ---------- Sale Price (discount applied) ----------
    def get_sale_price(self, obj):
        return obj.sale_price  # model property calculation

    # ---------- Total Price (quantity × sale_price) ----------
    def get_total(self, obj):
        return obj.total  # model property calculation

    def validate_user(self, value):
        if value.role != "basic_user":
            raise serializers.ValidationError(
                "Only buyer users can be assigned as cartitem author."
            )
        return value

    # ---------- Restrict update (user/books cannot change) ----------
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Buyers cannot change user or books
        if request.user.role == "basic_user":
            validated_data.pop("user", None)

        # Authors cannot change user or books (not allowed anyway)
        if request.user.role == "author":
            validated_data.pop("user", None)

        # Admin can change user, but cannot change books
        if request.user.role in ["admin"] or request.user.is_superuser:
            return super().update(instance, validated_data)

        return super().update(instance, validated_data)


# ---------------- Cart Create Serializer for Cart details----------------
class CartSerializer(serializers.ModelSerializer):
    # user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    mobile = serializers.CharField(source="user.mobile", read_only=True, default=None)

    items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="basic_user")
    )

    class Meta:
        model = Cart
        fields = "__all__"

    def get_items(self, obj):
        from .serializers import CartItemSerializer

        cart_items = obj.user.carts.all()
        return CartItemSerializer(cart_items, many=True).data

    def get_total_amount(self, obj):
        cart_items = obj.user.carts.all()
        return sum(item.total for item in cart_items)

    def validate_user(self, value):
        if value.role != "basic_user":
            raise serializers.ValidationError(
                "Only buyer users can be assigned as cart."
            )
        return value


# ---------------- User Serializer for User details----------------
class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[
            (CustomUser.AUTHOR, "Author"),
            (CustomUser.BASIC_USER, "Buyer"),
        ],
        required=True,
    )

    class Meta:
        model = CustomUser
        # fields = "__all__"
        exclude = ("groups", "user_permissions", "is_active")
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_active": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def validate_role(self, value):
        request = self.context.get("request")

        # Always allow serializer to work without request
        if not request:
            return value

        # REGISTER
        if request.method == "POST":
            if value == CustomUser.ADMIN:
                raise serializers.ValidationError("Admin users cannot be registered.")
            return value

        # UPDATE
        if request.method in ["PUT", "PATCH"]:
            user = request.user

            if not user.is_authenticated:
                raise serializers.ValidationError("Authentication required.")

            if not user.is_superuser:
                raise serializers.ValidationError("Role change is not allowed.")

        return value

    def create(self, validated_data):
        raise serializers.ValidationError(
            "User creation is only allowed via OTP-based registration."
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        role = validated_data.pop("role", None)

        if role and request and request.user.is_superuser:
            instance.role = role
            instance.is_staff = role == CustomUser.AUTHOR

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user


# ---------------- OTP Serializer for OTP details----------------


class SendOTPSerializer(serializers.Serializer):
    otp_via = serializers.ChoiceField(choices=[OTP.EMAIL, OTP.SMS], default=OTP.SMS)
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(max_length=10, required=False)

    def validate(self, data):
        if data["otp_via"] == OTP.EMAIL and not data.get("email"):
            raise serializers.ValidationError("Email required")

        if data["otp_via"] == OTP.SMS and not data.get("mobile"):
            raise serializers.ValidationError("Mobile required")

        if data.get("email") and data.get("mobile"):
            raise serializers.ValidationError(
                "Provide either email or mobile, not both"
            )

        # 🔒 RATE LIMIT (ANTI-SPAM)
        one_min_ago = timezone.now() - timedelta(minutes=1)

        if data.get("email"):
            if OTP.objects.filter(
                email=data["email"],
                purpose="registration",
                created_at__gte=one_min_ago,
            ).exists():
                raise serializers.ValidationError(
                    "Please wait 1 minute before requesting another OTP"
                )

        if data.get("mobile"):
            if OTP.objects.filter(
                mobile=data["mobile"],
                purpose="registration",
                created_at__gte=one_min_ago,
            ).exists():
                raise serializers.ValidationError(
                    "Please wait 1 minute before requesting another OTP"
                )

        # Already registered checks
        if data.get("email") and User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Email already registered")

        if data.get("mobile") and User.objects.filter(mobile=data["mobile"]).exists():
            raise serializers.ValidationError("Mobile already registered")

        return data

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        mobile = validated_data.get("mobile")
        otp_via = validated_data["otp_via"]

        # 🔥 delete old unused OTPs
        if otp_via == OTP.EMAIL:
            OTP.objects.filter(
                email=email, is_used=False, purpose="registration"
            ).delete()
        else:
            OTP.objects.filter(
                mobile=mobile, is_used=False, purpose="registration"
            ).delete()

        otp_code = generate_otp()  # e.g. 6-digit
        hashed_otp = make_password(otp_code)
        expiry_time = get_expiry_time()  # now + 5 minutes

        otp = OTP.objects.create(
            email=email,
            mobile=mobile,
            otp_via=otp_via,
            otp=hashed_otp,
            expires_at=expiry_time,
            purpose="registration",
        )

        # 🔔 send OTP
        if otp_via == OTP.EMAIL:
            send_email_otp(email, otp_code)
        else:
            send_sms_otp(mobile, otp_code)

        return otp


from django.contrib.auth.hashers import check_password


class VerifyOTPAndRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(max_length=10, required=False)
    otp = serializers.CharField(write_only=True)

    # user fields (same request me create hoga)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[CustomUser.AUTHOR, CustomUser.BASIC_USER])

    def validate(self, data):
        if not data.get("email") and not data.get("mobile"):
            raise serializers.ValidationError("Email or mobile required")

        if data.get("email") and data.get("mobile"):
            raise serializers.ValidationError(
                "Provide either email or mobile, not both"
            )

        otp_qs = OTP.objects.filter(
            is_used=False,
            purpose="registration",
        )

        if data.get("email"):
            otp_qs = otp_qs.filter(email=data["email"])

        if data.get("mobile"):
            otp_qs = otp_qs.filter(mobile=data["mobile"])

        otp_obj = otp_qs.order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("Invalid OTP")

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP expired")

        if not check_password(data["otp"], otp_obj.otp):
            raise serializers.ValidationError("Invalid OTP")

        data["otp_obj"] = otp_obj
        return data

    def create(self, validated_data):
        otp_obj = validated_data.pop("otp_obj")
        validated_data.pop("otp")
        password = validated_data.pop("password")
        role = validated_data.pop("role")

        # OTP consume
        otp_obj.is_used = True
        otp_obj.save()
        user = CustomUser.objects.create_user(
            password=password,
            role=role,
            **validated_data,
        )

        # Role-based flags
        if role == CustomUser.AUTHOR:
            user.is_staff = True

        user.save()
        return user

    # def create(self, validated_data):

    # # user create
    # user = CustomUser.objects.create_user(
    #     email=validated_data.get("email"),
    #     mobile=validated_data.get("mobile"),
    #     username=validated_data["username"],
    #     password=validated_data["password"],
    #     role=validated_data["role"],
    # )

    # if user.role == CustomUser.AUTHOR:
    #     user.is_staff = True
    #     user.save()

    # return user


"""

# Most used (important):

| Hook / Method              | Purpose                                             |
| -------------------------- | --------------------------------------------------- |
| `to_internal_value()`      | Convert raw input → Python data (validation step)   |
| `validate_empty_values()`  | Detect empty/missing values before validation       |
| `run_validation()`         | Full validation pipeline wrapper                    |
| `validate_<field>()`       | Field-level custom validation                       |
| `validate()`               | Object-level validation for multiple fields         |
| `to_representation()`      | Convert Python object → JSON output                 |
| `create()`                 | Create DB instance                                  |
| `update()`                 | Update DB instance                                  |
| `save()`                   | Wrapper that calls create/update                    |
| `is_valid()`               | Trigger validation and collect errors               |
| `get_fields()`             | Dynamically modify fields at runtime                |
| `get_validators()`         | Dynamically modify validators                       |
| `get_initial()`            | Initial form data (rare but exists)                 |
| `SerializerMethodField()`  | Dynamic serializer field with custom value          |
| `get_<field>()`            | Method that returns value for SerializerMethodField |
| `build_standard_field()`   | Auto-build basic fields                             |
| `build_relational_field()` | Auto-build relational fields                        |
| `build_nested_field()`     | Auto-build nested serializers                       |
| `build_property_field()`   | Build field from model property                     |
| `build_url_field()`        | Build HyperlinkedIdentityField                      |
| `build_unknown_field()`    | Handle fields not recognized                        |
| `get_attribute()`          | Fetch attribute from object safely                  |
| `build_field()`            | Master field builder calling above builders         |
| `run_validators()`         | Run all validators                                  |
| `get_value(dict)`          | Extract field value from request                    |
| `update_or_create()`       | Custom saving logic for nested input                |


"""
