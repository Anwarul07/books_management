from django.contrib import admin
from .models import (
    Books,
    Category,
    Author,
    Cart,
    CartItem,
    CustomUser,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# --- 1. Custom User  ---


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # --- List view ---
    list_display = (
        "username",
        "email",
        "role",
        "mobile",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
        "cover_image",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "mobile")
    ordering = ("username",)
    list_editable = ("role", "is_active")  # optional quick edit

    # --- Read-only fields ---
    readonly_fields = ("date_joined", "last_login")

    # --- Edit form ---
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Role & Contact Info",
            {
                "fields": ("role", "mobile"),
            },
        ),
        (
            "User Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                ),
                "classes": ("collapse",),  # collapsible in admin
            },
        ),
    )

    # --- Add new user form ---
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Role & Contact Info",
            {
                "fields": ("role", "mobile"),
            },
        ),
        (
            "User Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                ),
            },
        ),
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Restrict users shown in autocomplete
        queryset = queryset.filter(role="basic_user")
        return queryset, use_distinct


# Register CustomUser with CustomUserAdmin


# --- 2. Author Admin  ---
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = [
        "user",  # username
        "get_email",
        "get_mobile",
        "is_verified",
        "date_of_birth",
        "is_verified",
        "biography",
        "short_description",
        "date_of_birth",
    ]

    list_filter = ["is_verified"]
    search_fields = ["user__username", "user__email", "biography"]
    ordering = ["user__username"]

    fields = [
        "user",
        "is_verified",
        "biography",
        "short_description",
        "date_of_birth",
    ]

    # ---- Custom Display Methods ----
    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"

    def get_mobile(self, obj):
        return obj.user.mobile

    get_mobile.short_description = "Mobile"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(role="author")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# --- 3. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
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
    ]
    list_filter = ["origin"]
    search_fields = ["category_name", "description"]
    ordering = ["category_name"]

    # Form me fields ka order
    fields = [
        "category_name",
        "cover_image",
        "front_image",
        "behind_image",
        "side_image",
        "top_image",
        "bottom_image",
        "description",
        "origin",
    ]


# --- 2. Books Admin  ---
@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "author_name",
        "category_name",
        "isbn",
        "price",
        "discount",
        "sale_price",
        "availability",
        "language",
    ]

    list_filter = [
        "author",
        "category",
        "availability",
        "language",
        "binding_types",
        "edition",
        "publication_date",
    ]

    search_fields = [
        "title",
        "isbn",
        "description",
        "summary",
        "author__user__username",
        "category__category_name",
    ]

    ordering = ["title"]

    readonly_fields = [
        "created_at",
        "updated_at",
        "sale_price",
    ]

    fieldsets = (
        (
            "Book Details",
            {
                "fields": (
                    "title",
                    "author",
                    "category",
                    "total_pages",
                    "isbn",
                    "ratings",
                    "publication_date",
                )
            },
        ),
        (
            "Images",
            {
                "fields": (
                    "cover_image",
                    "front_image",
                    "behind_image",
                    "side_image",
                    "top_image",
                    "bottom_image",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "discount",
                    "sale_price",
                )
            },
        ),
        (
            "Extra Info",
            {
                "fields": (
                    "publications",
                    "availability",
                    "language",
                    "binding_types",
                    "edition",
                    "description",
                    "summary",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # Custom display fields
    def author_name(self, obj):
        return f"{obj.author.user.first_name} {obj.author.user.last_name}"

    def category_name(self, obj):
        return obj.category.category_name

    def sale_price(self, obj):
        return obj.sale_price

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            # Sirf Author role wale users show honge
            from .models import Author

            kwargs["queryset"] = Author.objects.filter(user__role="author")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# --- 4. CartItem Admin ---
@admin.register(CartItem)
class CartItemStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "books", "quantity", "added_at"]
    list_filter = ["user", "books"]
    search_fields = ["user__username", "books__title"]
    # autocomplete_fields = ["user", "books"]
    readonly_fields = ["added_at"]
    ordering = ["-added_at"]
    list_editable = ["quantity"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from .models import CustomUser

        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(role="basic_user")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# --- 4. Cart Admin  ---
@admin.register(Cart)
class CartStandaloneAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "user_email", "user_mobile"]
    search_fields = ["user__username", "user__email", "user__mobile"]
    list_filter = ["user"]
    ordering = ["user__username"]

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Mobile")
    def user_mobile(self, obj):
        return obj.user.mobile

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            from .models import CustomUser

            kwargs["queryset"] = CustomUser.objects.filter(role="basic_user")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
