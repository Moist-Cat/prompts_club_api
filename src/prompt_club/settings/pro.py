from ._base import *

DEBUG = False

X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 3600

CSRF_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True

ADMINS = ("MoistCat", "moistanonpy@gmail.com")

ALLOWED_HOSTS = ["moistcat.pythonanywhere.com"]
