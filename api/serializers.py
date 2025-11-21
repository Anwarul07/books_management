from django.contrib.auth.models import User
from rest_framework import serializers
from decimal import Decimal
import json
from django.db.models import F
from .models import (
    Books,
    Author,
    Category,
    CartItem,
    Cart,
)


# Book read details for assign only category detail in any seralizers
class BooksReadSerializer(serializers.ModelSerializer):

    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale_price = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = Books
        fields = [
            "id",
            "title",
            "author",
            "author_name",  # Added for convenience
            "category",
            "category_name",  # Added for convenience
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
            "sale_price",  # Matched to model @property
            "publications",
            "availablity",
            "language",
            "binding_types",
            "edition",
            "description",
            "summary",
            "publication_date",
        ]

    def get_author_name(self, val):
        if val:
            return val.author.author_name


# Author read to assign details of author only in any seralizers
class AuthorReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "author_name",
            "email",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "contact",
            "is_verified",
            "biography",
            "register_date",
            "date_of_Birth",
            "short_description",
        ]


# Category read details for assign only category detail in any seralizers
class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",  # Added 'id' for nesting/read operations
            "category_name",
            "description",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "origin",
        ]


# Book creating seralizer for create book
class BooksCreateSerializer(serializers.ModelSerializer):
    author_details = AuthorReadSerializer(read_only=True, source="author")
    category_details = serializers.SerializerMethodField()

    category_name = serializers.StringRelatedField(source="category")
    author_name = serializers.SerializerMethodField()

    availablity = serializers.CharField(read_only=True)
    sale_price = serializers.SerializerMethodField()

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
            "availablity",
            "language",
            "binding_types",
            "edition",
            "description",
            "summary",
            "publication_date",
            "created_at",
            "updated_at",
            "author_details",
            "category_details",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "author_name",
            "category_name",
            "sale_price",
            "author_details",
            "category_details",
        ]

    def get_author_name(self, val):
        if val:
            return val.author.author_name

    def get_sale_price(self, val):
        if val:
            price = val.price
            discount = Decimal(val.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total

    def get_category_details(self, obj):
        return CategoryReadSerializer(obj.category).data


# Author creating seralizer for create author
class AuthorCreateSerializer(serializers.ModelSerializer):
    books_of_author = BooksReadSerializer(many=True, read_only=True)
    totalbook = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    category_of_books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "url",
            "id",
            "author_name",
            "email",
            "contact",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "is_verified",
            "biography",
            "register_date",
            "date_of_Birth",
            "short_description",
            "books_of_author",
            "totalbook",
            "category_of_books",
            "totalcategory",
        ]
        read_only_fields = [
            "register_date",
            "is_verified",
            "books_of_author",
            "totalbook",
            "category_of_books",
            "totalcategory",
        ]

    def get_totalbook(self, val):
        if val:
            return val.books_of_author.count()

    def get_totalcategory(self, val):
        if val:
            return (
                val.books_of_author.values_list("category", flat=True)
                .distinct()
                .count()
            )

    def get_category_of_books(self, val):
        if val:
            unique_categories = Category.objects.filter(
                category_of_books__author=val
            ).distinct()
            return CategoryReadSerializer(unique_categories, many=True).data


# Category creating seralizer for create book
class CategoryCreateSerializer(serializers.ModelSerializer):
    from django.db.models import F

    category_of_books = BooksReadSerializer(many=True, read_only=True)

    totalbook = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    totalauthors = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "url",
            "category_name",
            "description",
            "cover_image",
            "front_image",
            "behind_image",
            "side_image",
            "top_image",
            "bottom_image",
            "origin",
            "category_of_books",
            "totalbook",
            "authors",
            "totalauthors",
        ]
        read_only_fields = [
            # Fields that are output-only
            "category_of_books",
            "totalbook",
            "authors",
            "totalauthors",
        ]

    def get_totalbook(self, val):
        if val:
            print(val.category_of_books)
            return val.category_of_books.count()

    def get_authors(self, val):
        if val:
            data = (
                val.category_of_books.annotate(
                    ids=F("author__id"),
                    name=F("author__author_name"),
                    email=F("author__email"),
                )
                .values(
                    "ids",
                    "name",
                    "email",
                )
                .distinct()
            )
            return list(data)

    def get_totalauthors(self, val):
        if val:

            return (
                val.category_of_books.values_list("author", flat=True)
                .distinct()
                .count()
            )


# Cart create seralizers is for creating cart
class CartItemSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user", read_only=True)
    book_title = serializers.CharField(source="books.title", read_only=True)

    price = serializers.SerializerMethodField()
    discount = serializers.DecimalField(
        source="books.discount", max_digits=10, decimal_places=2, read_only=True
    )
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    sale_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            # "url",
            "id",
            "user",  # The FK ID to the Cart (Writable for creation/update)
            "books",  # The FK ID to the Book (Writable for creation/update)
            "username",  # Read-only output
            "book_title",
            "price",
            "discount",
            "sale_price",
            "quantity",  # Writable field
            "total",
            "added_at",  # Read-only output
        ]
        read_only_fields = ["added_at"]

    def get_price(self, val):
        if val.books:
            return val.books.price

    def update(self, instance, validated_data):
        # Prevent users from changing the book or cart FKs during an update.
        if "book" in validated_data:
            validated_data.pop("book")
        if "cart" in validated_data:
            validated_data.pop("cart")

        return super().update(instance, validated_data)


# cart list of a user serializers
class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["url", "user", "username", "items", "sub_total"]
        read_only_fields = ["username"]

    def get_items(self, cart_list_instance):
        context = self.context
        cart_items_queryset = cart_list_instance.user.carts.all()
        return CartItemSerializer(cart_items_queryset, many=True, context=context).data

    def get_sub_total(self, val):
        cart_items = val.user.carts.all()
        sub_total = sum(item.total for item in cart_items)
        return round(sub_total, 2)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "url",
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "date_joined",
        ]
        extra_kwargs = {
            "date_joined": {"read_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # 1. Use pop() to safely remove the password from validated_data
        password = validated_data.pop("password")

        # 2. Create the user object without the password first
        user = User.objects.create(**validated_data)

        # 3. Use set_password and save to securely hash the password
        user.set_password(password)
        user.save()

        return user

    # def create(self, validated_data):
    #     print(validated_data)
    #     user = User.objects.create_user(**validated_data)
    #     return user
