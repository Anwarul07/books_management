from django.contrib.auth.models import User
from rest_framework import serializers
from decimal import Decimal
from .models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

# from django.contrib.auth import get_user_model
# User = get_user_model()

from .models import (
    Books,
    Author,
    Category,
    CartItem,
    Cart,
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
        fields = [
            "url",
            "id",
            "title",
            "author",
            "author_name",
            "category",
            "category_name",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "total_pages",
            "isbn",
            "ratings",
            "price",
            "discount",
            "sale_price",
            "publications",
            "availability",
            "language",
            "binding_types",
            "edition",
            "description",
            "summary",
            "publication_date",
        ]

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
        fields = [
            # "id",
            "url",
            "user_id",
            "role",
            "user",
            "author_name",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "is_verified",
            "biography",
            "short_description",
            "date_of_birth",
        ]
        read_only_fields = [
            "is_verified",
        ]

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
        fields = [
            "id",
            "category_name",
            "description",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "origin",
            "created_at",
            "updated_at",
        ]


# ---------------- Book Create Serializer for Book details----------------
class BooksCreateSerializer(serializers.ModelSerializer):
    author_details = AuthorReadSerializer(read_only=True, source="author")
    category_details = CategoryReadSerializer(read_only=True, source="category")

    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale_price = serializers.SerializerMethodField()
    viewed_by = serializers.SerializerMethodField()

    # Author assignment restricted to users with role "author"
    # author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    class Meta:
        model = Books
        fields = [
            "url",
            "id",
            "title",
            "author",
            "author_name",
            "category",
            "category_name",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "total_pages",
            "isbn",
            "ratings",
            "price",
            "discount",
            "sale_price",
            "publications",
            "availability",
            "language",
            "binding_types",
            "edition",
            "description",
            "summary",
            "publication_date",
            "viewed_by",
            "created_at",
            "updated_at",
            "author_details",
            "category_details",
        ]
        read_only_fields = [
            "author_name",
            "author_details",
            "category_name",
            "category_details",
            "sale_price",
            # "availability",
            "created_at",
            "updated_at",
            "viewed_by",
        ]

    def get_author_name(self, obj):
        return f"{obj.author.user.first_name} {obj.author.user.last_name}"

    def get_sale_price(self, obj):
        discount_percentage = Decimal(obj.discount or 0) / Decimal(100)
        total = obj.price * (Decimal(1) - discount_percentage)
        return round(total, 2)

    def validate_author(self, value):
        if value.user.role != CustomUser.AUTHOR:
            raise serializers.ValidationError(
                "The associated user must have the role 'author'."
            )
        return value

    def get_viewed_by(self, obj):
        user = self.context["request"].user
        return user.username

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user

        if not user.is_superuser:
            fields.pop("availability")  # hide sensitive field
        return fields


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
    books_of_author = BooksReadSerializer(many=True, read_only=True)

    # Aggregates
    totalbooks = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    category_of_books = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(role="author")
    )

    class Meta:
        model = Author
        fields = [
            "url",
            "user_id",
            "role",
            "user",
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "biography",
            "date_of_birth",
            "short_description",
            "is_verified",
            "books_of_author",
            "totalbooks",
            "category_of_books",
            "totalcategory",
        ]

        read_only_fields = [
            "username",
            "email",
            "mobile",
            "is_verified",
            "books_of_author",
            "totalbooks",
            "category_of_books",
            "totalcategory",
        ]

    def validate_user(self, value):
        if value.role != "author":
            raise serializers.ValidationError(
                "Only Author users can be assigned as book author."
            )
        return value

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
        fields = [
            "category_name",
            "description",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "origin",
            "created_at",
            "updated_at",
            "category_of_books",
            "totalbook",
            "authors",
            "totalauthors",
        ]
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
        fields = [
            # "url",
            "id",
            "user",
            "username",
            "first_name",
            "last_name",
            "books",  # FK ID (write only)
            "book_title",
            "book_price",
            "book_discount",
            "sale_price",
            "quantity",
            "total",
            "added_at",
        ]
        read_only_fields = ["added_at"]

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
        validated_data.pop("user", None)
        validated_data.pop("books", None)
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
        fields = [
            # "url",
            "id",
            "user",
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "items",
            "total_amount",
        ]

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


# ---------------- User Create Serializer for User details----------------
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
        fields = [
            "id",
            # "url",
            "role",
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "password",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "date_joined",
            "last_login",
        ]
        extra_kwargs = {
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
            "password": {"write_only": True, "required": True},
        }

    def validate_user(self, value):
        if value.role == "admin":
            raise serializers.ValidationError("Admin users can't be register.")
        return value

    def create(self, validated_data):
        print(validated_data)
        password = validated_data.pop("password")
        role = validated_data.pop("role")
        print("Password raw", password)
        print("Role raw", role)
        user = CustomUser.objects.create_user(
            password=password,
            role=role,
            **validated_data,
        )
        print("Password", password)
        print("Role", role)

        if role == CustomUser.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        elif role == CustomUser.AUTHOR:
            user.is_staff = True

        user.save()
        return user

    # def create(self, validated_data):
    #     user = User.objects.create_user(**validated_data)
    #     return user


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
