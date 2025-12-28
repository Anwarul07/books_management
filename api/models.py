from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.conf import settings
from django.core.exceptions import ValidationError


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

    # --- Authentication --
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile", "username"]

    # --- String Representation ---
    def __str__(self):
        return self.username


# ---OTP Model ---


class OTP(models.Model):

    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"

    PURPOSE_CHOICES = (
        (REGISTRATION, "Registration"),
        (LOGIN, "Login"),
        (PASSWORD_RESET, "Password Reset"),
    )
    EMAIL = "email"
    SMS = "sms"

    OTP_VIA = (
        (EMAIL, "Email"),
        (SMS, "SMS/Text Message"),
    )

    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=10, blank=True, null=True)

    otp_via = models.CharField(max_length=10, choices=OTP_VIA, default=EMAIL)
    otp = models.CharField(max_length=128)

    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        default=REGISTRATION,
    )
    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def clean(self):
        if not self.email and not self.mobile:
            raise ValidationError("Either email or mobile is required")

    def __str__(self):
        return f"OTP({self.email or self.mobile})"


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        related_name="author_profile",
    )
    biography = models.TextField(max_length=200)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField()
    short_description = models.TextField()

    def __str__(self):
        return self.user.username


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
        "Category", on_delete=models.PROTECT, related_name="category_of_books"
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
        unique_together = ("author", "title")


# ---Cartitem user Model ---


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


"""

| No.    | Hook / Method                             | Purpose / Use Case (Short Description)                 |
| ------ | ----------------------------------------- | ------------------------------------------------------ |
| **1**  | `__init__()`                              | Model object load/create hote hi initialize karna      |
| **2**  | `save()`                                  | Record create/update se pehle custom logic chalana     |
| **3**  | `delete()`                                | Record delete se pehle custom logic chalana            |
| **4**  | `clean()`                                 | Custom model-level validation                          |
| **5**  | `clean_fields()`                          | Field-by-field validation                              |
| **6**  | `validate_unique()`                       | Unique constraint manually validate karna              |
| **7**  | `full_clean()`                            | clean_fields + clean + validate_unique full validation |
| **8**  | `from_db()`                               | DB se object load hone par hook trigger hota hai       |
| **9**  | `get_absolute_url()`                      | Object ka canonical URL return karna                   |
| **10** | `__str__()`                               | Model ka readable string representation                |
| **11** | `get_FOO_display()`                       | Choice field ka human-readable text return             |
| **12** | `get_next_by_<datefield>()`               | Date field ke basis par next record lana               |
| **13** | `get_previous_by_<datefield>()`           | Date field ke basis par previous record                |
| **14** | `prepare_database_save()`                 | Database save ke time low-level override hook          |
| **15** | `serializable_value(field)`               | Serialization ke time field value customize            |
| **16** | `Meta` class                              | Ordering, db_table, constraints, indexes define        |
| **17** | `Manager.get_queryset()`                  | Custom queryset logic control                          |
| **18** | `Custom Manager Methods`                  | Model-level business logic (e.g., `published()`)       |
| **19** | `pre_save` (signal)                       | Save se bilkul pehle trigger hota hai                  |
| **20** | `post_save` (signal)                      | Save hone ke turant baad trigger hota hai              |
| **21** | `pre_delete` (signal)                     | Delete se pehle trigger hota hai                       |
| **22** | `post_delete` (signal)                    | Delete ke baad trigger hota hai                        |
| **23** | `post_init` (signal)                      | Model object initialize hote hii trigger hota hai      |
| **24** | `m2m_changed` (signal)                    | ManyToMany relation change hote hi trigger             |
| **25** | `post_migrate` (signal)                   | Migration complete hone ke baad trigger                |
| **26** | `bulk_create()`                           | Multiple objects ek hi query me create karna           |
| **27** | `refresh_from_db()`                       | Database se latest data reload karna                   |
| **28** | `save_base()`                             | save() ka low-level core version                       |
| **29** | `check()`                                 | Model validation (errors return karta hai)             |
| **30** | `validate_constraints()`                  | Constraints (Unique, CheckConstraint) validate         |
| **31** | `natural_key()`                           | Natural key export karne ka hook                       |
| **32** | `unique_error_message()`                  | Unique constraint fail hone par custom message         |
| **33** | `create()`                                | Object create karta hai, save() auto                   |
| **34** | `get_or_create()`                         | Agar object hai → return, nahi → create                |
| **35** | `update_or_create()`                      | Update ya create logic                                 |
| **36** | `all()` / `filter()` / `exclude()`        | Queryset filter hooks                                  |
| **37** | `annotate()`                              | Calculated field add (e.g., sales count)               |
| **38** | `aggregate()`                             | Full queryset summary (e.g., total revenue)            |
| **39** | `select_related()` / `prefetch_related()` | ForeignKey/M2M fast fetch, optimize queries            |


"""
