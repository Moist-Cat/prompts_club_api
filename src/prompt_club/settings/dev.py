from ._base import *

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

CACHES = {
	"default": {
		"BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
		"LOCATION": "127.0.0.1:11211"
	}
}


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = "127.0.0.1"
