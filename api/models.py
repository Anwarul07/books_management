from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


# Category models
class Category(models.Model):
    ORIGIN_CHOICES = [
        ("india", "Indian"),
        ("foreign", "Foreign"),
    ]
    category_name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to="category/")
    front_image = models.ImageField(upload_to="category/")
    behind_image = models.ImageField(upload_to="category/")
    side_image = models.ImageField(upload_to="category/")
    top_image = models.ImageField(upload_to="category/")
    bottom_image = models.ImageField(upload_to="category/")
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="india")

    def __str__(self):
        return self.category_name


class Author(models.Model):
    author_name = models.CharField(max_length=30, null=False, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    contact = models.CharField(max_length=10)
    cover_image = models.ImageField(upload_to="author/")
    front_image = models.ImageField(upload_to="author/")
    behind_image = models.ImageField(upload_to="author/")
    side_image = models.ImageField(upload_to="author/")
    top_image = models.ImageField(upload_to="author/")
    bottom_image = models.ImageField(upload_to="author/")
    biography = models.TextField(max_length=200)
    is_verified = models.BooleanField(default=False)
    register_date = models.DateField(auto_now_add=True)
    date_of_Birth = models.DateField()
    short_description = models.TextField()

    def __str__(self):
        return self.author_name


class Books(models.Model):
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
        ("softcover", "Softcover/Papercover"),
        ("stiching", "Stiching"),
        ("spiral", "Spiral"),
    ]
    EDITION_CHOICES = [
        ("limited", "Limited"),
        ("bulk", "Bulk"),
        ("special", "Special"),
    ]

    title = models.CharField(max_length=30, unique=True, null=False, blank=False)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="books_of_author"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_of_books"
    )
    cover_image = models.ImageField(upload_to="books/")
    front_image = models.ImageField(upload_to="books/")
    behind_image = models.ImageField(upload_to="books/")
    side_image = models.ImageField(upload_to="books/")
    top_image = models.ImageField(upload_to="books/")
    bottom_image = models.ImageField(upload_to="books/")
    total_pages = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], null=False, blank=False
    )
    isbn = models.CharField(max_length=17, unique=True, null=True, blank=True)
    ratings = models.DecimalField(
        max_length=2,
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True,
    )
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
        max_length=20, choices=AVAILABILITY_CHOICES, default="pending"
    )
    language = models.CharField(
        max_length=20, choices=LANGUAGE_CHOICES, default="hindi"
    )
    binding_types = models.CharField(
        max_length=20, choices=BINDING_CHOICES, default="softcover"
    )
    edition = models.CharField(max_length=20, choices=EDITION_CHOICES, default="bulk")
    description = models.TextField()
    summary = models.TextField(null=True, blank=True)
    publication_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sale_price(self):
        base_price = self.price
        discount_percentage = self.discount or 0

        if discount_percentage > 0:
            discount_rate_decimal = Decimal(discount_percentage) / Decimal(100)
            return round(base_price * (Decimal(1) - discount_rate_decimal), 2)
        return base_price

    def __str__(self):
        return self.title


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    books = models.ForeignKey(
        Books, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        unique_together = ("user", "books")

    @property
    def sale_price(self):
        base_price = self.books.price
        discount_percentage = self.books.discount or 0

        if discount_percentage > 0:
            discount_rate_decimal = Decimal(discount_percentage / Decimal(100))
            return round(base_price * (Decimal(1) - discount_rate_decimal), 2)
        return base_price

    @property
    def total(self):
        return round(self.sale_price * self.quantity, 2)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return self.user.username
