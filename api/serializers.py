from rest_framework import serializers
from .models import Books, Author, Category, Cart, Wishlist
from decimal import Decimal
import json
from django.db.models import F


class AuthorRead(serializers.ModelSerializer):
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


class BooksSerializers(serializers.ModelSerializer):
    sale = serializers.SerializerMethodField()

    class Meta:
        model = Books
        fields = [
            "url",
            "id",
            "books_name",
            "title",
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
            "language",
            "binding_types",
            "edition",
            "description",
            "summary",
            "publication_date",
            "created_at",
            "updated_at",
            "author",
            "category",
        ]

    def get_sale(self, val):
        if val:
            price = val.price
            discount = Decimal(val.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total


class CategoryRead(serializers.ModelSerializer):
    # book_category = BooksSerializers(many=True, read_only=True)
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


class BooksListSerializers(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.StringRelatedField(source="category")
    sale = serializers.SerializerMethodField()
    author_details = AuthorRead(read_only=True, source="author")
    category_details = CategoryRead(read_only=True, source="category")

    class Meta:
        model = Books
        fields = [
            "url",
            "id",
            "books_name",
            "title",
            "author",
            "category",
            "author_name",
            "category_name",
            "availablity",
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


class CategoryReadCategory(serializers.ModelSerializer):
    book_category = BooksSerializers(many=True, read_only=True)
    totalbooks = serializers.SerializerMethodField()

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
            "book_category",
            "totalbooks",
        ]

    def get_totalbook(self, val):
        if val:
            return val.book_author.count()


class CategorySerializers(serializers.ModelSerializer):
    from django.db.models import F

    book_category = BooksSerializers(many=True, read_only=True)
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


class AuthorSerializers(serializers.ModelSerializer):
    totalbook = serializers.SerializerMethodField()
    totalcategory = serializers.SerializerMethodField()
    book_author = BooksSerializers(many=True, read_only=True)
    author_categories = serializers.SerializerMethodField()
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
            "book_author",
            "totalbook",
            "author_categories",
            "totalcategory",
        ]

    def get_totalbook(self, val):
        if val:
            return val.book_author.count()

    def get_totalcategory(self, val):
        if val:
            return val.book_author.values_list("category", flat=True).distinct().count()

    def get_author_categories(self, val):
        if val:
            data = (
                val.book_author.annotate(
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


class WishlistSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField(source="book.books_name")
    cart = serializers.StringRelatedField(source="cart.user.author_name")
    sale = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = [
            "url",
            "id",
            "cart",
            "book",
            "quattity",
            "sale",
            "book",
            "total_price",
            "added_at",
            "updated_at",
        ]

    def get_sale(self, val):
        if val.book:
            price = val.book.price
            discount = Decimal(val.book.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total

    def get_total_price(self, val):
        quantity = val.quattity
        sale = self.get_sale(val)
        total_price = sale * quantity
        return total_price


class CartSerializer(serializers.ModelSerializer):
    wishlists = WishlistSerializer(read_only=True, many=True)
    user = serializers.StringRelatedField(source="user.author_name")

    class Meta:
        model = Cart
        fields = [
            "url",
            "id",
            "user",
            "created_at",
            "updated_at",
            "wishlists",
        ]


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "url",
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


class WishCreateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = [
            "url",
            "id",
            "book",
            "cart",
            "quattity",
            "added_at",
            "updated_at",
        ]
