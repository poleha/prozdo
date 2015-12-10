"""
Django settings for prozdo project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1b%%&2h^(f%4u%1bw64n_x$vhb-b5#t(5fn%x+gkic169rm=t7'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['127.0.0.1', 'prozdo.ru']

#DATETIME_FORMAT = 'd.m.Y H:i' not required since we use l10n


try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

if HOSTNAME in ['ubuntu']:
    DEBUG = True
    COMPRESS_ENABLED = False
    HTML_MINIFY = True
    CACHE_ENABLED = True
    DEBUG_TOOLBAR = False
else:
    DEBUG = False
    DEBUG_TOOLBAR = False
    CACHE_ENABLED = True
    COMPRESS_ENABLED = True
    HTML_MINIFY = True

EXCLUDE_FROM_MINIFYING = ('^admin/',)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'mptt',
    'allauth.socialaccount.providers.vk',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'prozdo_main',
    'sorl.thumbnail',
    'django.contrib.redirects',
    'compressor',
    'reversion',
    'ckeditor',
    'ckeditor_uploader',
    #'cacheops',
    'django_mobile',
    'haystack',
    'contact_form',
)

MIDDLEWARE_CLASSES = (

    'django.middleware.http.ConditionalGetMiddleware',
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.gzip.GZipMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'super_model.middleware.SetClientIpMiddleware',
    'super_model.middleware.SetUserKeyMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

ROOT_URLCONF = 'prozdo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'prozdo_main/templates/prozdo_main')],
        #'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'super_model.context_processors.debug',
                'super_model.context_processors.show_ad',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_mobile.context_processors.flavour',
            ],
        },
    },
]


WSGI_APPLICATION = 'prozdo.wsgi.application'
"""
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TEST': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'test.sqlite3')
        }
    }
}
"""


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'prozdo',
        'USER': 'kulik',
        'PASSWORD': 'ZaX369Exn',
       'HOST': '127.0.0.1',
       'PORT': '5432',
        'CONN_MAX_AGE': 500,
        },


}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = '1'
SITE_URL = 'http://prozdo.ru'
DEFAULT_FROM_EMAIL = 'Prozdo.ru <info@prozdo.ru>'
SERVER_EMAIL = 'info@prozdo.ru'
INTERNAL_IPS = ['127.0.0.1']
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'  # URL для медии в шаблонах
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
#SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_CACHE_ALIAS = "default"
SESSION_SAVE_EVERY_REQUEST = False
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True


#**************<<<<<
POST_COMMENTS_PAGE_SIZE = 30
POST_LIST_PAGE_SIZE = 48

APPEND_SLASH = True

#**************>>>>>>>>>>


#allauth
LOGIN_REDIRECT_URLNAME = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 30
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_PASSWORD_MIN_LENGTH = 6
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_ADAPTER  = "prozdo_main.adapter.ProzdoSocialAccountAdapter"
ACCOUNT_ADAPTER = "prozdo_main.adapter.ProzdoAccountAdapter"


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

#CACHES = {
#    'default': {
#        'BACKEND': 'prozdo_main.backends.ProzdoMemcachedCacheCacheBackend',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}


CACHES = {
    "default": {
        'BACKEND': 'prozdo_main.backends.ProzdoRedisCacheBackend',
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            'DB': 2,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        }
    }
}


#CACHES = {
#    "default": {
#        "BACKEND": "prozdo_main.backends.ProzdoRedisCacheBackend",
#        "LOCATION": "redis://127.0.0.1:6379/2",
#    }
#}

THUMBNAIL_BACKEND = 'prozdo_main.backends.SEOThumbnailBackend'
THUMBNAIL_PREFIX = 'images/'
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
THUMBNAIL_REDIS_DB = 2



STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

BEST_COMMENTS_DAYS = 100

CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"

#CACHE_MIDDLEWARE_SECONDS = 60 * 60



CACHEOPS_REDIS = {
    'host': 'localhost', # redis-server is on same machine
    'port': 6379,        # default redis port
    'db': 1,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended

}



#CACHEOPS_DEFAULTS = {
#    'timeout': CACHEOPS_DURATION
#}


if DEBUG_TOOLBAR:

    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.remove('django.middleware.gzip.GZipMiddleware')
    MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES)
    INSTALLED_APPS += ('debug_toolbar',)

    DEBUG_TOOLBAR_PATCH_SETTINGS = True
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]



    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES

    DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}


if CACHE_ENABLED and not DEBUG:

    TEMPLATES[0]['OPTIONS']['loaders'] = [
            #'django_mobile.loader.Loader',
            ('django.template.loaders.cached.Loader',
                  [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
            ],
                ),
        ]
else:
       TEMPLATES[0]['OPTIONS']['loaders'] = [
                    #'django_mobile.loader.Loader',
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
        ]

"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level':'WARNING',
            'class':'logging.FileHandler',
            'filename': BASE_DIR + "/../logfile",
        },
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'logfile']
    },
}
"""

AUTO_APPROVE_EMAILS = ['approve@approve.me']
AUTO_DONT_APPROVE_EMAILS = ['dont-approve@dont-approve.me']

ADMINS = (('Alex Poleha', 'info@prozdo.ru'),)

PUBLISH_COMMENT_WITHOUT_APPROVE_KARM = 20


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}


DEFAULT_THUMBNAIL_QUALITY = 75




CACHED_METHOD_SPECIAL_CASES = {
    'django.core.handlers.wsgi.WSGIRequest': ('user.pk', 'session.prozdo_key', 'client_ip')
}

CACHED_VIEW_DURATION = 60 * 60 * 24 * 7
CACHED_PROPERTY_DURATION = 60 * 60 * 24 * 7
CACHED_METHOD_DURATION = 60 * 60
HISTORY_EXISTS_DURATION = 60 * 60 * 24 * 7
HISTORY_EXISTS_BY_COMMENT_DURATION = 60 * 60 * 24


BASE_POST_CLASS = 'prozdo_main.models.Post'
BASE_HISTORY_CLASS = 'prozdo_main.models.History'
BASE_MAIL_CLASS = 'prozdo_main.models.Mail'
BASE_USER_PROFILE_CLASS = 'prozdo_main.models.UserProfile'

SITE_NAME = 'Prozdo.ru'



POST_TYPE_DRUG = 1
POST_TYPE_BLOG = 2
POST_TYPE_FORUM = 3
POST_TYPE_COSMETICS = 4
POST_TYPE_COMPONENT = 5
POST_TYPE_BRAND = 6
POST_TYPE_DRUG_DOSAGE_FORM = 7
POST_TYPE_COSMETICS_DOSAGE_FORM = 8
POST_TYPE_COSMETICS_LINE = 9
POST_TYPE_COSMETICS_USAGE_AREA = 10
POST_TYPE_DRUG_USAGE_AREA = 11
POST_TYPE_CATEGORY = 12


POST_TYPES = (
    (POST_TYPE_DRUG, 'Препарат'),
    (POST_TYPE_BLOG, 'Блог'),
    (POST_TYPE_FORUM, 'Форум'),
    (POST_TYPE_COMPONENT, 'Компонент'),
    (POST_TYPE_COSMETICS, 'Косметика'),
    (POST_TYPE_BRAND, 'Бренд'),
    (POST_TYPE_DRUG_DOSAGE_FORM, 'Форма выпуска препарата'),
    (POST_TYPE_COSMETICS_DOSAGE_FORM, 'Форма выпуска косметики'),
    (POST_TYPE_COSMETICS_LINE, 'Линия косметики'),
    (POST_TYPE_COSMETICS_USAGE_AREA, 'Область применения косметики'),
    (POST_TYPE_DRUG_USAGE_AREA, 'Област применения препарата'),
    (POST_TYPE_CATEGORY, 'Категория'),
)

SUPER_MODEL_KEY_NAME = 'prozdo_key'


USER_ROLE_REGULAR = 1
USER_ROLE_AUTHOR = 2
USER_ROLE_DOCTOR = 3
USER_ROLE_ADMIN = 33

USER_ROLES = (
        (USER_ROLE_REGULAR, 'Обычный пользователь'),
        (USER_ROLE_AUTHOR, 'Автор'),
        (USER_ROLE_DOCTOR, 'Врач'),
        (USER_ROLE_ADMIN, 'Админ'),
    )