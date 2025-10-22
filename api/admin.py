from django.contrib import admin
from .models import Books


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
