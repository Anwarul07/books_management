from rest_framework import serializers
from .models import Books, Author, Category
from decimal import Decimal


# class authorread(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fields = [
#             "id",
#             "author_name",
#             "email",
#             "contact",
#             "cover_image",
#             "biography",
#             "register_date",
#             "Date_of_Birth",
#             "short_description",
#         ]


# class categoryread(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = [
#             "category_name",
#             "description",
#             "origin",
#         ]


class BooksSerializers(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()
    #author = authorread(read_only=True)
    # category = categoryread(read_only=True)

    class Meta:
        model = Books
        fields = [
            "url",
            "id",
            "books_name",
            "title",
            "author_name",
            "category_name",
            "total_pages",
            "ratings",
            "cover_image",
            "price",
            "discount",
            "sale",
            "publications",
            "availablity",
            "language",
            "binding_types",
            "edition",
            "description",
            "publication_date",
            "created_at",
            "updated_at",
            "author",
            "category",
        ]

    def get_category_name(self, val):
        if val:
            return val.category.category_name
        val

    def get_author_name(self, val):
        if val:
            return val.author.author_name
        val

    def get_sale(self, val):
        if val:
            price = val.price
            discount = Decimal(val.discount / 100)
            discounAmount = Decimal(price * discount)
            total = price - discounAmount
            return total


class CategorySerializers(serializers.ModelSerializer):
    book_category = BooksSerializers(many=True, read_only=True)
    totalbooks = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "url",
            "category_name",
            "description",
            "origin",
            "book_category",
            "totalbooks",
        ]

    def get_totalbooks(self, val):
        if val:
            return val.book_category.count()


class AuthorSerializers(serializers.ModelSerializer):
    totalbook = serializers.SerializerMethodField()
    book_author = BooksSerializers(many=True, read_only=True)
    category = CategorySerializers(read_only=True, many=True)  # add in model if  needed

    class Meta:
        model = Author
        fields = [
            "url",
            "id",
            "author_name",
            "email",
            "contact",
            "cover_image",
            "biography",
            "register_date",
            "Date_of_Birth",
            "short_description",
            "book_author",
            "category",
            "totalbook",
        ]

    def get_totalbook(self, val):
        if val:
            return val.book_author.count()
