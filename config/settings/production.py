"""
Production settings for deployment
"""

from .base import *
import dj_database_url
import os

DEBUG = False

# ALLOWED_HOSTS = [
#     '.onrender.com',
#     'walshoney-mgmt.onrender.com',  # Your actual domain
# ]

ALLOWED_HOSTS = [
    '.railway.app', ''
]

# Parse DATABASE_URL from environment
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True

# Static files with Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'