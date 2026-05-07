import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default or []

    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv(
    "GATEWAY_SECRET_KEY",
    os.getenv("SECRET_KEY", "django-insecure-dev-gateway-service-only-change-me"),
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
DEBUG = env_bool("GATEWAY_DEBUG", env_bool("DEBUG", ENVIRONMENT != "production"))
ALLOWED_HOSTS = env_list(
    "GATEWAY_ALLOWED_HOSTS",
    env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "testserver"]),
)

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "rest_framework",
    "gateway",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gateway_service.urls"
WSGI_APPLICATION = "gateway_service.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_CLASSES": [
        "gateway.throttles.JwtUserOrIPRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": os.getenv("USER_RATE_LIMIT", "50/min"),
    },
}

IDENTITY_SERVICE_URL = os.getenv("IDENTITY_SERVICE_URL", "http://localhost:8000")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
GATEWAY_REQUEST_TIMEOUT = float(os.getenv("GATEWAY_REQUEST_TIMEOUT", "10"))

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
