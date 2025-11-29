from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings


# ---Custom user Model ---
class CustomUser(AbstractUser):
    # --- Roles ---
    ADMIN = "admin"
    AUTHOR = "author"
    BASIC_USER = "basic_user"
    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (AUTHOR, "Author"),
        (BASIC_USER, "Basic User"),
    )

    # --- User Info ---
    mobile = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=BASIC_USER)

    # --- Optional Images ---
    cover_image = models.ImageField(upload_to="users/", blank=True, null=True)
    front_image = models.ImageField(upload_to="users/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="users/", blank=True, null=True)
    side_image = models.ImageField(upload_to="users/", blank=True, null=True)
    top_image = models.ImageField(upload_to="users/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="users/", blank=True, null=True)

    # --- Custom Manager ---
    objects = CustomUserManager()

    # --- Authentication ---
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "mobile"]

    # --- String Representation ---
    def __str__(self):
        return self.username


# ---Category Model ---
class Category(models.Model):
    ORIGIN_CHOICES = [
        ("india", "Indian"),
        ("foreign", "Foreign"),
    ]

    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    # Images (optional)
    cover_image = models.ImageField(upload_to="category/", blank=True, null=True)
    front_image = models.ImageField(upload_to="category/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="category/", blank=True, null=True)
    side_image = models.ImageField(upload_to="category/", blank=True, null=True)
    top_image = models.ImageField(upload_to="category/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="category/", blank=True, null=True)

    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="india")

    class Meta:
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


# ---Author user Model ---
class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="author_profile",
    )
    biography = models.TextField(max_length=200)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField()
    short_description = models.TextField()

    def __str__(self):
        return self.user.username


from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


# ---Book Model ---
class Books(models.Model):

    # ------------ Choices ------------
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("maintenance", "Under Maintenance"),
        ("pending", "Pending for Approval"),
    ]

    LANGUAGE_CHOICES = [
        ("hindi", "Hindi"),
        ("urdu", "Urdu"),
        ("english", "English"),
    ]

    BINDING_CHOICES = [
        ("hardcover", "Hardcover"),
        ("softcover", "Softcover / Papercover"),
        ("stitching", "Stitching"),
        ("spiral", "Spiral"),
    ]

    EDITION_CHOICES = [
        ("limited", "Limited"),
        ("bulk", "Bulk"),
        ("special", "Special"),
    ]

    # ------------ Main Fields ------------
    title = models.CharField(max_length=50, unique=True)

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books_of_author",
    )

    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="category_of_books"
    )

    # ------------ Images ------------
    cover_image = models.ImageField(upload_to="books/", blank=True, null=True)
    front_image = models.ImageField(upload_to="books/", blank=True, null=True)
    behind_image = models.ImageField(upload_to="books/", blank=True, null=True)
    side_image = models.ImageField(upload_to="books/", blank=True, null=True)
    top_image = models.ImageField(upload_to="books/", blank=True, null=True)
    bottom_image = models.ImageField(upload_to="books/", blank=True, null=True)

    # ------------ Book Details ------------
    total_pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    isbn = models.CharField(max_length=17, unique=True, null=True, blank=True)

    ratings = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True,
    )

    price = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(0)]
    )

    discount = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

    publications = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Anwar Publications",
    )

    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="pending"
    )

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="hindi",
    )

    binding_types = models.CharField(
        max_length=20,
        choices=BINDING_CHOICES,
        default="softcover",
    )

    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, default="bulk")

    description = models.TextField()
    summary = models.TextField(null=True, blank=True)

    publication_date = models.DateField()

    # ------------ Auto Fields ------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------ Computed Field ------------
    @property
    def sale_price(self):
        """Price after discount"""
        if not self.discount:
            return self.price

        discount_decimal = Decimal(self.discount) / Decimal(100)
        return round(self.price * (1 - discount_decimal), 2)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


# ---Cartitem user Model ---
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts"
    )
    books = models.ForeignKey(
        "Books", on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "books")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} → {self.books.title}"

    # --- Calculated Sale Price (single book price after discount)
    @property
    def sale_price(self):
        price = Decimal(self.books.price)
        discount = Decimal(self.books.discount or 0)

        if discount > 0:
            discount_rate = discount / Decimal(100)
            return round(price * (Decimal(1) - discount_rate), 2)

        return round(price, 2)

    # --- Total = sale price × quantity
    @property
    def total(self):
        return round(self.sale_price * self.quantity, 2)


# ---Cart Model ---
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )

    def __str__(self):
        return self.user.username
