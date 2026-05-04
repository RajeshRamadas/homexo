"""
HOMEXO — Luxury Real Estate Portal
Django Settings
"""

from pathlib import Path
import os
import logging

# Load .env file automatically (python-dotenv is already installed via requirements)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    pass  # dotenv not installed — rely on shell environment variables

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-homexo-change-this-in-production-use-env-variable')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ─── APPLICATIONS ────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'social_django',
]

LOCAL_APPS = [
    'accounts',
    'properties',
    'enquiries',
    'blog',
    'testimonials',
    'wishlist',
    'pages',
    'legal_services',
    # 'chatbot',  # ── Disabled: re-enable when upgrading to 4 GB Droplet ──
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'homexo.urls'

# ─── AUTHENTICATION BACKENDS ─────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# ─── TEMPLATES ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pages.context_processors.global_context',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'homexo.wsgi.application'

# ─── DATABASE ─────────────────────────────────────────────────────────────────
# PostgreSQL with pgvector for both website & RAG chatbot.
# Set DB_ENGINE=django.db.backends.postgresql in .env for production.
_DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': _DB_ENGINE,
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        # Enable pgvector extension on first migrate (PostgreSQL only)
        **({
            'OPTIONS': {
                'options': '-c search_path=public',
            }
        } if _DB_ENGINE == 'django.db.backends.postgresql' else {}),
    }
}

# ─── AUTH ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ─── SOCIAL AUTH (Google & Facebook OAuth) ───────────────────────────────────
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY    = os.environ.get('GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE  = ['openid', 'email', 'profile']

SOCIAL_AUTH_FACEBOOK_KEY    = os.environ.get('FACEBOOK_APP_ID', '')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
SOCIAL_AUTH_FACEBOOK_SCOPE  = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,email,first_name,last_name',
}

SOCIAL_AUTH_LOGIN_REDIRECT_URL      = '/accounts/profile/'
SOCIAL_AUTH_LOGIN_ERROR_URL         = '/accounts/login/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL   = '/accounts/profile/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/accounts/profile/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'accounts.pipeline.get_or_create_user',          # custom: email-based lookup
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'accounts.pipeline.save_profile_data',           # custom: sync name fields
)

# Raise an error if GOOGLE/FB keys are missing in production (fail fast on misconfiguration)
SOCIAL_AUTH_RAISE_EXCEPTIONS = not DEBUG

# ─── INTERNATIONALISATION ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ─── STATIC & MEDIA ───────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Limit in-memory file upload size (Nginx already enforces 20MB via client_max_body_size)
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB

# Sessions expire after 7 days of inactivity
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days

# ─── DJANGO REST FRAMEWORK ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Restrict in production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
# In production, allow the domains from ALLOWED_HOSTS
if not DEBUG:
    CORS_ALLOWED_ORIGINS += [
        f'https://{host}' for host in ALLOWED_HOSTS if host not in ('', '*')
    ]

# ─── EMAIL — Zoho Mail (–smtp.zoho.in) ───────────────────────────────────────────────
# Zoho SMTP: host=smtp.zoho.in, port=587 (TLS) or port=465 (SSL).
# Use an App Password from Zoho Mail → Settings → Security → App Passwords.
# DEFAULT_FROM_EMAIL must exactly match EMAIL_HOST_USER in Zoho.
# In dev, set EMAIL_BACKEND=console to print emails to terminal instead of sending.
EMAIL_BACKEND       = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.zoho.in')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'   # use port 465 + SSL instead of TLS
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')            # Zoho App Password
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@homexo.in')  # must match EMAIL_HOST_USER
ENQUIRY_NOTIFICATION_EMAIL = os.environ.get('ENQUIRY_NOTIFICATION_EMAIL', 'enquiries@homexo.in')

# ─── AI / RAG (Urvashi Chatbot) ──────────────────────────────────────────────
# Claude via Anthropic API + local sentence-transformers embeddings
LLM_API_KEY          = os.environ.get('LLM_API_KEY', '')
LLM_MODEL            = os.environ.get('LLM_MODEL', 'claude-haiku-4-5-20251001')
EMBEDDING_MODEL      = os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
EMBEDDING_DIM        = int(os.environ.get('EMBEDDING_DIM', 384))
RAG_TOP_K            = int(os.environ.get('TOP_K', 5))
RAG_SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.35))

# ─── TWILIO (Phone OTP) ───────────────────────────────────────────────────────
# Sign up at https://www.twilio.com and get a trial phone number.
TWILIO_ACCOUNT_SID  = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN   = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')  # e.g. +12015551234
# Leave blank in dev — OTPs will print to the terminal console instead.

# ─── CACHE ────────────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'homexo-cache',
    }
}

# ─── LOGGING ──────────────────────────────────────────────────────────────────
# Suppress noisy Chrome DevTools auto-probe from the dev server log.
class _IgnoreChromeDevTools(logging.Filter):
    def filter(self, record):
        return '/.well-known/appspecific/com.chrome.devtools' not in record.getMessage()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'ignore_chrome_devtools': {
            '()': _IgnoreChromeDevTools,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['ignore_chrome_devtools'],
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ─── PRODUCTION SECURITY ──────────────────────────────────────────────────────
# These only activate when DEBUG=False (i.e., on the live server).
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Trust the HTTPS origins declared in ALLOWED_HOSTS for CSRF
    CSRF_TRUSTED_ORIGINS = [
        f'https://{host}' for host in ALLOWED_HOSTS if host not in ('', '*')
    ]

    # Reuse DB connections across requests (seconds)
    DATABASES['default']['CONN_MAX_AGE'] = 60
    # Validate pooled connections before use — prevents stale connection errors
    # when Postgres restarts while Gunicorn workers are running.
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
