import os
import environ
from pathlib import Path

# ------------------------------
# Base Paths
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ------------------------------
# SECURITY
# ------------------------------
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG')
ALLOWED_HOSTS = [
    'localhost',
    'rekjrc.com',
    'www.rekjrc.com',
    '10.1.1.63',
    '127.0.0.1',
]

# ------------------------------
# Stripe
# ------------------------------
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# ------------------------------
# Installed Apps
# ------------------------------
INSTALLED_APPS = [
    # Django default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_user_agents',
    'django_extensions',
    'phonenumber_field',
    'widget_tweaks',
    # Your apps
    "builds",
    "chat_app",
    "clubs",
    "drivers",
    "events",
    "humans",
    "locations",
    "posts",
    "profiles",
    "races",
    "sponsors",
    "stores",
    "stripe_app",
    "support",
    "teams",
    "tracks",
	"urls_app",
]

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

# ------------------------------
# URL Config
# ------------------------------
ROOT_URLCONF = "rekjrc.urls"

# ------------------------------
# Templates
# ------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Put your HTML templates here
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "rekjrc.context.device_type",
                "sponsors.context_processors.sponsors_context",
            ],
        },
    },
]

# For Django 5.x+ the format requires scheme (http or https)
CSRF_TRUSTED_ORIGINS = [
    "https://www.rekjrc.com",
    "https://rekjrc.com",
    "http://10.1.1.63",
    "http://127.0.0.1",
    "http://localhost",
    "https://aa97a0f2ef11.ngrok-free.app",
]

# ------------------------------
# WSGI
# ------------------------------
WSGI_APPLICATION = "rekjrc.wsgi.application"

# ------------------------------
# Database
# ------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# ------------------------------
# Password Validation
# ------------------------------
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

# ------------------------------
# Logging
# ------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # Silence the development server request logs (404, etc)
        'django.server': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Silence Django request logs (404s)
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# ------------------------------
# Internationalization
# ------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static & Media files
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------
# Default Primary Key Type
# ------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# Custom User Model
# ------------------------------
AUTH_USER_MODEL = "humans.Human"

# settings.py
LOGIN_REDIRECT_URL = '/'  # redirect to homepage after login
LOGOUT_REDIRECT_URL = '/'  # optional: redirect to homepage after logout
