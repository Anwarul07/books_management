from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    ORIGIN_CHOICES = [
        ("india", "Indian"),
        ("foreign", "Foreign"),
    ]
    category_name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(max_length=100)
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="india")


class Author(models.Model):
    author_name = models.CharField(max_length=30, null=False, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    cover_image = models.ImageField(upload_to="author/", null=True, blank=True)
    biography = models.TextField(max_length=200)
    register_date = models.DateField()
    contact = models.IntegerField()
    Date_of_Birth = models.DateField()
    short_description = models.TextField()


class Books(models.Model):
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("maintenance", "Under Maintenance"),
        ("pending", "Pending for Approval"),
    ]
    LANGUAGE_CHOICES = [
        ("hindi", "Hindi"),
        ("urdu", "English"),
        ("english", "English"),
    ]
    BINDING_CHOICES = [
        ("hardcover", "Hardcover"),
        ("softcover", "Softcover/Papercover"),
        ("stiching", "Stiching"),
        ("spiral", "Spiral"),
    ]
    EDITION_CHOICES = [
        ("limited", "Limited"),
        ("bulk", "Bulk"),
        ("special", "Special"),
    ]

    books_name = models.CharField(max_length=30, unique=True, null=False, blank=False)
    title = models.CharField(max_length=30, unique=True, null=False, blank=False)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="book_author"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="book_category"
    )
    total_pages = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=False, blank=False
    )
    ratings = models.DecimalField(
        max_length=2,
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True,
    )
    cover_image = models.ImageField(upload_to="", null=True, blank=True)
    price = models.DecimalField(
        max_length=5,
        max_digits=5,
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(0.0)],
    )
    discount = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    publications = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Anwar Publications",
    )
    availablity = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="available"
    )
    language = models.CharField(
        max_length=20, choices=LANGUAGE_CHOICES, default="hindi"
    )
    binding_types = models.CharField(
        max_length=20, choices=BINDING_CHOICES, default="softcover"
    )
    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, default="bulk")
    description = models.TextField()
    publication_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
