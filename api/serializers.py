from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Books, Author, Category, Cart, CartList
from decimal import Decimal
import json
from django.db.models import F


# Book read details for assign only category detail in any seralizers
class BooksReadSerializers(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale = serializers.SerializerMethodField()

    class Meta:
        model = Books
        fields = [
            "books_name",
            "title",
            "author",
            "author_name",
            "category",
            "category_name",
            "total_pages",
            "isbn",
            "ratings",
            "cover_image",
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "price",
            "discount",
            "sale",
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

    def get_sale(self, val):
        if val:
            price = val.price
            discount = Decimal(val.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total


# Author read to assign details of author only in any seralizers
class AuthorReadSerailizers(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "author_name",
            "email",
            "cover_image",
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "is_verified",
            "biography",
            "register_date",
            "Date_of_Birth",
            "short_description",
        ]


# Category read details for assign only category detail in any seralizers
class CategoryReadSeralizers(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "category_name",
            "description",
            "cover_image",
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "origin",
        ]


# Book creating seralizer for create book
class BooksCreateSerializers(serializers.ModelSerializer):
    author_details = AuthorReadSerailizers(read_only=True, source="author")
    category_details = CategoryReadSeralizers(read_only=True, source="category")

    availablity = serializers.CharField(read_only=True)
    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale = serializers.SerializerMethodField()

    class Meta:
        model = Books
        fields = [
            "books_name",
            "title",
            "author",
            "author_name",
            "category",
            "category_name",
            "total_pages",
            "isbn",
            "ratings",
            "cover_image",
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "price",
            "discount",
            "sale",
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

    def get_author_name(self, val):
        if val:
            return val.author.author_name

    def get_sale(self, val):
        if val:
            price = val.price
            discount = Decimal(val.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total


# Author creating seralizer for create author
class AuthorCreateSerializers(serializers.ModelSerializer):
    books_of_author = BooksReadSerializers(many=True, read_only=True)

    totalbook = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    category_of_books = serializers.SerializerMethodField()
    # book_category = CategorySerializers(
    #     read_only=True, source="book_author__category"
    # )  # add in model if  needed

    class Meta:
        model = Author
        fields = [
            "url",
            "id",
            "author_name",
            "email",
            "contact",
            "cover_image",
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "biography",
            "register_date",
            "Date_of_Birth",
            "short_description",
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
            data = (
                val.books_of_author.annotate(
                    ids=F("category__id"),
                    name=F("category__category_name"),
                    descriptions=F("category__description"),
                )
                .values(
                    "ids",
                    "name",
                    "descriptions",
                    # Add any other fields you need here
                )
                .distinct()
            )
            return list(data)


# Category creating seralizer for create book
class CategoryCreateSerializers(serializers.ModelSerializer):
    from django.db.models import F

    category_of_books = BooksReadSerializers(many=True, read_only=True)

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
            "cover_front",
            "cover_behind",
            "cover_top",
            "cover_bottom",
            "cover_side",
            "origin",
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
                    # Add any other fields you need here
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
class CartCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user", read_only=True)
    books_name = serializers.CharField(source="books", read_only=True)
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "url",
            "id",
            "user",
            "username",
            "books",
            "books_name",
            "price",
            "discount",
            "sale_price",
            "quantity",
            "total",
            "added_at",
        ]

    def get_price(self, val):
        if val.books:
            return val.books.price

    def get_discount(self, val):
        if val.books:
            return val.books.discount

    def get_sale_price(self, val):
        if val.books.price:
            price = val.books.price
            discount = Decimal(val.books.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total

    def get_total(Self, val):
        if val.books.price:
            price = val.books.price
            discount = Decimal(val.books.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total * val.quantity


# cart list of a user serializers
class CartListCreateSerializers(serializers.ModelSerializer):
    carts = CartCreateSerializer(many=True, read_only=True)

    class Meta:
        model = CartList
        fields = ["url", "id", "user", "carts"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "id", "username", "password"]
        # extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
