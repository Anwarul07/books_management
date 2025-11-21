# filters.py
import django_filters
from .models import Books


class BooksFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    availablity = django_filters.CharFilter(
        field_name="availablity", lookup_expr="exact"
    )
    language = django_filters.CharFilter(field_name="language", lookup_expr="exact")
    binding_types = django_filters.CharFilter(
        field_name="binding_types", lookup_expr="exact"
    )
    publications = django_filters.CharFilter(
        field_name="publications", lookup_expr="icontains"
    )
    edition = django_filters.CharFilter(field_name="edition", lookup_expr="icontains")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(
        field_name="category__category_name", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author__author_name", lookup_expr="icontains"
    )


class CategoryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category_name", lookup_expr="icontains"
    )
    oringin = django_filters.CharFilter(field_name="origin", lookup_expr="icontains")
