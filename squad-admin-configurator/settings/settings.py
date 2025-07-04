from pathlib import Path

import toml

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG = toml.load(BASE_DIR / "config.toml")

BASE_URL = CONFIG["SERVER"]["BASE_URL"]

SECRET_KEY = CONFIG["DJANGO"]["SECRET_KEY"]

DEBUG = CONFIG["DJANGO"]["DEBUG"]

ALLOWED_HOSTS = CONFIG["DJANGO"]["ALLOWED_HOSTS"]

CSRF_TRUSTED_ORIGINS = CONFIG["DJANGO"]["CSRF_TRUSTED_ORIGINS"]

INSTALLED_APPS = [
    "adminactions",
    "jet",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "access",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "admin_ordering",
    "auth_api.apps.AuthApiConfig",
    "server_rotations.apps.ServerRotationsConfig",
    "server_rotations_api.apps.ServerRotationsApiConfig",
    "server_admins.apps.ServerAdminsConfig",
    "api.apps.ApiConfig",
    "django_cron",
    "django_cron_proxy.apps.DjangoCronProxyConfig",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "settings.wsgi.application"

if CONFIG["DJANGO"]["SQLITE"]:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": CONFIG["DJANGO"]["POSTGRES_DB"],
            "USER": CONFIG["DJANGO"]["POSTGRES_USER"],
            "PASSWORD": CONFIG["DJANGO"]["POSTGRES_PASSWORD"],
            "HOST": CONFIG["DJANGO"]["POSTGRES_HOST"],
            "PORT": CONFIG["DJANGO"]["POSTGRES_PORT"],
        }
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ADMINS_CONFIG_DIR = BASE_DIR / CONFIG["ADMINS"]["ADMINS_CONFIG_DIR"]
ROTATIONS_CONFIG_DIR = BASE_DIR / CONFIG["ROTATIONS"]["ROTATIONS_CONFIG_DIR"]

CRON_CLASSES = [
    "api.cron.CreateAdminsConfig",
    "server_admins.cron.DisablingPrivilegedByEndTime",
    "server_admins.cron.DisablingServerPrivilegedByEndTime",
    "server_admins.cron.DisablingServerPrivilegedPacksByEndTime",
    "server_rotations_api.cron.CreateRotationsFiles",
]

DJANGO_CRON_DELETE_LOGS_OLDER_THAN = CONFIG["CRON"]["DELETE_LOGS_OLDER_THAN"]

TIME_FORMAT = "%d-%m-%y %H:%M:%S"

DISCORD = CONFIG["DISCORD"]
HMAC_VALIDATION = CONFIG["HMAC_VALIDATION"]

ADMIN_SITE_HEADER = CONFIG["ADMIN_SITE"]["ADMIN_SITE_HEADER"]
ADMIN_SITE_TITLE = CONFIG["ADMIN_SITE"]["ADMIN_SITE_TITLE"]
ADMIN_INDEX_TITLE = CONFIG["ADMIN_SITE"]["ADMIN_INDEX_TITLE"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("permissions.AdvancedDjangoModelPermissions",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Squad Admin Configurator",
    "DESCRIPTION": "Панель управления привилегированными пользователями в Squad",
    "VERSION": "1.7.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

X_FRAME_OPTIONS = "sameorigin"

JET_SIDE_MENU_COMPACT = True
