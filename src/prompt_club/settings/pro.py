from ._base import *

DEBUG = False
CACHES = {
	  'default': {
	    'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
	    # TIMEOUT is not the connection timeout! It's the default expiration
	    # timeout that should be applied to keys! Setting it to `None`
	    # disables expiration.
	    'TIMEOUT': 60*60 # 1 hour,
	    'LOCATION': get_secret('MEMCACHIER_SERVERS'),
	    'OPTIONS': {
	      'binary': True,
	      'username': get_secret('MEMCACHIER_USERNAME'),
	      'password': get_secret('MEMCACHIER_PASSWORD'),
	      'behaviors': {
	        # Enable faster IO
	        'no_block': True,
	        'tcp_nodelay': True,
	        # Keep connection alive
	        'tcp_keepalive': True,
	        # Timeout settings
	        'connect_timeout': 2000, # ms
	        'send_timeout': 750 * 1000, # us
	        'receive_timeout': 750 * 1000, # us
	        '_poll_timeout': 2000, # ms
	        # Better failover
	        'ketama': True,
	        'remove_failed': 1,
	        'retry_timeout': 2,
	        'dead_timeout': 30,
	        }
	    }
    }
}

X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_SECONDS = 3600

CSRF_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True

ADMINS = ("MoistCat", "moistanonpy@gmail.com")

ALLOWED_HOSTS = ["moistcat.pythonanywhere.com"]
