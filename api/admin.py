from django.contrib import admin
from .models import (
    Books,
    Category,
    Author,
    Cart,
    CartItem,
)


# --- 1. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "category_name", "description", "origin"]
    list_filter = ["origin"]
    search_fields = ["category_name", "description"]
    ordering = ["category_name"]
    fields = ["category_name", "description", "origin"]


# --- 2. Author Admin  ---
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "author_name",
        "email",
        "contact",
        "is_verified",
        "register_date",
        "date_of_Birth",
    ]

    list_filter = ["is_verified", "register_date"]
    search_fields = ["author_name", "email", "biography"]
    ordering = ["author_name"]
    fields = [
        "author_name",
        "email",
        "contact",
        "is_verified",
        "biography",
        "short_description",
        "date_of_Birth",
        "register_date",
    ]
    readonly_fields = ["register_date", "id"]


# --- 3. Books Admin  ---
@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "title",
        "author",
        "category",
        "price",
        "discount",
    ]
    list_filter = [
        "category",
        "author",
    ]
    search_fields = ["title", "description"]
    ordering = ["title"]

    fields = [
        "title",
        "author",
        "category",
        "description",
        "price",
        "discount",
    ]


# --- 4. Cart Admin  ---
@admin.register(Cart)
class CartStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]
    search_fields = ["user__username"]
    list_filter = [
        "user",
    ]
    ordering = ["user__username"]
    # fields = ["user"]


@admin.register(CartItem)
class CartItemStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "books", "quantity"]
    search_fields = ["user__username", "books__title"]
