import six.moves.urllib.parse
import os

import dj_database_url
import environ

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = env.bool('DJANGO_DEBUG', default=True)
if DEBUG:
    ALLOWED_HOSTS = []
    SECRET_KEY = 'itsdebugwhocares'

else:
    ALLOWED_HOSTS = ['api.dlogr.com', ]
    SECRET_KEY = env('DJANGO_SECRET_KEY')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dlogr_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dlogr_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'


########
# HEROKU
db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

########
# CUSTOM
ROOT_DIR = environ.Path(__file__) - 2  # (/a/b/myfile.py - 2 = /a/)

INTERNAL_APPS = [
    'main',

]
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
    'anymail',
] + INTERNAL_APPS

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTH_USER_MODEL = 'main.Customer'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/')
CACHE_DEFAULT_TIME_TO_LIVE_IN_SECONDS = env.int('CACHE_DEFAULT_TIME_TO_LIVE_IN_SECONDS', default=60 * 60 * 24)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'DB': 0,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'PASSWORD': six.moves.urllib.parse.urlparse(REDIS_URL).password,
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                # Hobby redisToGo on heroku supports max. of 10 connections, 8 is safe limit
                # given other monitoring clients may be connected.
                'max_connections': env.int('REDIS_MAX_CONNECTIONS', default=8),
                'timeout': 20,
            }
        }
    }
}
CACHE_PREFIX = {
    'VERIFY_ACCOUNT': 'verify-account',
    'RESET_PASSWORD': 'reset-password',
}

WEB_CLIENT_URLS = {
    'VERIFY_ACCOUNT': 'https://www.dlogr.com/auth/verify-account?token={key}&joined={joined}',
    'RESET_PASSWORD': 'https://www.dlogr.com/auth/change-forgotten-password/?reset_token={key}',
}

DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default='Dlogr Support <support@dlogr.com>')
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default='[Dlogr]')
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
SERVER_EMAIL = 'support@dlogr.com'

if env.bool('ROLLBAR_ENABLED', default=False):
    MIDDLEWARE = MIDDLEWARE + [  # pragma: no cover
        'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
    ]

    ROLLBAR = {  # pragma: no cover
        'access_token': env('ROLLBAR_ACCESS_TOKEN'),
        'environment': env('ENVIRONMENT_NAME'),
        'root': str(ROOT_DIR),
    }

if env.bool('POSTMARK_ENABLED', default=False):
    EMAIL_BACKEND = "anymail.backends.postmark.PostmarkBackend"  # pragma: no cover
    ANYMAIL = {  # pragma: no cover
        "POSTMARK_SERVER_TOKEN": env('POSTMARK_API_KEY'),
    }

if env.bool('FORCE_HTTPS', default=False):
    SECURE_SSL_REDIRECT = True  # pragma: no cover
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # pragma: no cover
