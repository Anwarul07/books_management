from django.contrib import admin
from .models import Books, Category, Author, Cart, CartList


# Category model admin configuration
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
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
    list_filter = ["category_name", "origin"]
    search_fields = ["category_name", "description"]
    ordering = ["category_name"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author_name",
        "email",
        "cover_image",
        "cover_front",
        "cover_behind",
        "cover_top",
        "cover_bottom",
        "cover_side",
        "biography",
        "is_verified",
        "register_date",
        "contact",
        "Date_of_Birth",
        "short_description",
    ]
    list_filter = ["author_name", "is_verified"]
    search_fields = ["author_name", "email"]
    ordering = ["author_name"]


# Book model admin configuration
@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "books_name",
        "title",
        "ratings",
        "cover_image",
        "price",
        "publications",
        "availablity",
        "language",
        "binding_types",
        "edition",
        "description",
        "publication_date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["books_name", "title"]
    search_fields = ["title", "books_name"]
    ordering = ["books_name"]


# Cart model admin configuration
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "books",
        "quantity",
        "added_at",
        "updated_at",
    ]
    list_filter = ["user"]
    search_fields = ["books"]
    ordering = ["books"]


# CartList model admin configuration
@admin.register(CartList)
class CartListAdmin(admin.ModelAdmin):
    list_display = ["user"]
    list_filter = ["user"]
    search_fields = ["'user"]
    ordering = ["user"]
