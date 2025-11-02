from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Books, Author, Category, Cart
from decimal import Decimal
import json
from django.db.models import F


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


# Category details for assign only category detail in any seralizers
class CategoryReadSeralizers(serializers.ModelSerializer):
    # book_category = BooksCreateSerializers(many=True, read_only=True)
    # totalbooks = serializers.SerializerMethodField()

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
            # "book_category",
            # "totalbooks",
        ]


# Book details for assign only category detail in any seralizers
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


# Author serilizer
class AuthorCreateSerializers(serializers.ModelSerializer):
    totalbook = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    books_of_author = BooksReadSerializers(many=True, read_only=True)
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


class BooksCreateSerializers(serializers.ModelSerializer):
    availablity = serializers.CharField(read_only=True)
    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale = serializers.SerializerMethodField()

    author_details = AuthorReadSerailizers(read_only=True, source="author")
    category_details = CategoryReadSeralizers(read_only=True, source="category")

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


class CategoryCreateSerializers(serializers.ModelSerializer):
    from django.db.models import F

    book_category = BooksReadSerializers(many=True, read_only=True)
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
            "book_category",
            "totalbook",
            "authors",
            "totalauthors",
        ]

    def get_totalbook(self, val):
        if val:
            print(val.book_category)
            return val.book_category.count()

    def get_authors(self, val):
        if val:
            data = (
                val.book_category.annotate(
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

            return val.book_category.values_list("author", flat=True).distinct().count()


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source="user.author_name")

    class Meta:
        model = Cart
        fields = [
            "url",
            "id",
            "created_at",
            "updated_at",
        ]


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "url",
            "id",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        # extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
