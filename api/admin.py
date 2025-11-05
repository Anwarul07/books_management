from django.contrib import admin
from .models import (
    Books,
    Category,
    Author,
    Cart,
    CartItem,
    CategoryImage,
    AuthorImage,
    BooksImage,
)

# --- INLINES ---


class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 1
    fields = ["image", "image_type"]


class AuthorImageInline(admin.TabularInline):
    model = AuthorImage
    extra = 1
    fields = ["image", "image_type"]


class BooksImageInline(admin.TabularInline):
    model = BooksImage
    extra = 1
    fields = ["image", "image_type"]


# --- 1. Category Admin (Correct) ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "category_name", "description", "origin"]
    list_filter = ["origin"]
    search_fields = ["category_name", "description"]
    ordering = ["category_name"]
    fields = ["category_name", "description", "origin"]
    inlines = [CategoryImageInline]


# --- 2. Author Admin (FIXED) ---
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
    inlines = [AuthorImageInline]

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


# --- 3. Books Admin (FIXED) ---
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

    inlines = [BooksImageInline]

    fields = [
        "title",
        "author",
        "category",
        "description",
        "price",
        "discount",
    ]


# --- 4. Cart Admin (FIXED) ---
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
