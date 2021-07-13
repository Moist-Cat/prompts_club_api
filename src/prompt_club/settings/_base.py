"""
Django settings for prompt_club project.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path
import json
import sys
from django.core.exceptions import ImproperlyConfigured
from apps.core.versioning import get_git_changeset_timestamp

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
"""
EXTERNAL_BASE = os.path.join(BASE_DIR, "externals")
EXTERNAL_LIBS_PATH = os.path.join(EXTERNAL_BASE, "libs")
EXTERNAL_APPS_PATH = os.path.join(EXTERNAL_BASE, "apps")
sys.path = ["", EXTERNAL_LIBS_PATH, EXTERNAL_APPS_PATH] + sys.path
"""


with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
    secrets = json.loads(f.read())


def get_secret(setting):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = f"Set the {setting} secret variable"
        raise ImproperlyConfigured(error_msg)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "0.0.0.0",
]


# Application definition

INSTALLED_APPS = [
    # contributed
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "taggit",
    "rest_framework",
    "rest_framework.authtoken",
    "memcache_status",
    # local
    "apps.scenario.apps.ScenarioConfig",
    "apps.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "prompt_club.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "prompt_club.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_secret("DATABASE_NAME"),
        "USER": get_secret("DATABASE_USER"),
        "PASSWORD": get_secret("DATABASE_PASSWORD"),
        "HOST": get_secret("DATABASE_HOST"),
    },
    "TEST": {"ENGINE": "django.db.backends.mysql"}
}


# Password validation
# https://docs.djangoproject.com/en/3.1/topics/auth/passwords/#password-validation

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

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "site_static"),
]


# media
timestamp = get_git_changeset_timestamp(BASE_DIR)
STATIC_URL = f"/static/{timestamp}/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

EMAIL_HOST = get_secret("EMAIL_HOST")
EMAIL_PORT = get_secret("EMAIL_PORT")
EMAIL_HOST_USER = get_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD")

# Cache
CACHES = {
          'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
          }
    }

# Rest Framework
REST_FRAMEWORK = {
    # Permissions
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Authentication
    #
    # Uses both Token and session since it is easier to 
    # use the API via browser with the first one.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication"
    ],
    # Throttling
    #
    # To prevent DDoS attacks and to slow down enter-mashing shizos.
    # Since most queries will be cached, regular users should not 
    # feel a thing. Re-Sending the request when it gets throttled is 
    # a detail to have in mind when doing the front-end, though.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle"
    ],
    # Subject to change. Although with smart caching system it shouldn't 
    # go much lower.
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/s',
        'anon': '7/s',
    },
    # Shemas
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
