from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Category models 
class Category(models.Model):
    ORIGIN_CHOICES = [
        ("india", "Indian"),
        ("foreign", "Foreign"),
    ]
    category_name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to="category/", null=True, blank=True)
    cover_front = models.ImageField(upload_to="category/", null=True, blank=True)
    cover_behind = models.ImageField(upload_to="category/", null=True, blank=True)
    cover_top = models.ImageField(upload_to="category/", null=True, blank=True)
    cover_bottom = models.ImageField(upload_to="category/", null=True, blank=True)
    cover_side = models.ImageField(upload_to="category/", null=True, blank=True)
    origin = models.CharField(max_length=10, choices=ORIGIN_CHOICES, default="india")

    def __str__(self):
        return self.category_name


class Author(models.Model):
    author_name = models.CharField(max_length=30, null=False, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    cover_image = models.ImageField(upload_to="author/", null=True, blank=True)
    cover_front = models.ImageField(upload_to="author/", null=True, blank=True)
    cover_behind = models.ImageField(upload_to="author/", null=True, blank=True)
    cover_top = models.ImageField(upload_to="author/", null=True, blank=True)
    cover_bottom = models.ImageField(upload_to="author/", null=True, blank=True)
    cover_side = models.ImageField(upload_to="author/", null=True, blank=True)
    biography = models.TextField(max_length=200)
    is_verified = models.BooleanField(default=False)
    register_date = models.DateField()
    contact = models.IntegerField()
    Date_of_Birth = models.DateField()
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
    isbn = models.CharField(max_length=14, unique=True, null=True, blank=True)
    ratings = models.DecimalField(
        max_length=2,
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True,
    )
    cover_image = models.ImageField(upload_to="", null=True, blank=True)
    cover_front = models.ImageField(upload_to="", null=True, blank=True)
    cover_behind = models.ImageField(upload_to="", null=True, blank=True)
    cover_top = models.ImageField(upload_to="", null=True, blank=True)
    cover_bottom = models.ImageField(upload_to="", null=True, blank=True)
    cover_side = models.ImageField(upload_to="", null=True, blank=True)
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

    def __str__(self):
        # Return the field that holds the name
        return self.books_name


class Cart(models.Model):
    user = models.OneToOneField(
        Author, on_delete=models.CASCADE, null=True, blank=True, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.author_name if self.user else 'Anonymous'}"


class Wishlist(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="wishlists")
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="wishlisted")
    quattity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.summary} in wishlist of {self.cart.user.author_name if self.cart.user else 'Anonymous'}"

