from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api.apps.ApiConfig",
    "rest_framework",
    "corsheaders",
    "django_filters",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Bookselling.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Bookselling.wsgi.application"


import dj_database_url
import os

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///books.sqlite3",
        conn_max_age=600,
        ssl_require=bool(os.getenv("DATABASE_URL")),
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = [
    "http://localhost:4000",
    "http://127.0.0.1:4000",
    "https://anwarbook.onrender.com",
]
CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:4000",
    "http://127.0.0.1:4000",
    "https://anwarbook.onrender.com",
]


CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_ALL_ORIGINS = False

import os

MEDIA_URL = "/media/"  # URL path for media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Directory to store media files

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"


# settings.py
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]
}


AUTH_USER_MODEL = "api.CustomUser"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # fallback
    "api.auth_backends.EmailOrMobileBackend",
]


# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": [
#         "rest_framework.authentication.SessionAuthentication",
#         # "rest_framework.authentication.TokenAuthentication",
#         # Add other authentication classes as needed, e.g., 'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
#     # "DEFAULT_PERMISSION_CLASSES": [
#     #     "rest_framework.permissions.IsAuthenticated",
#     #     # Add other global permission classes if desired
#     # ],
# }


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = "BookSelling App <yourmail@gmail.com>"


TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER")
