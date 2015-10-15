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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1b%%&2h^(f%4u%1bw64n_x$vhb-b5#t(5fn%x+gkic169rm=t7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'mptt',

    'allauth.socialaccount.providers.vk',
    #'allauth.socialaccount.providers.twitter',
    #'allauth.socialaccount.providers.odnoklassniki',
    #'allauth.socialaccount.providers.openid',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    'prozdo_main',
    #'multi_image_upload',
     'sorl.thumbnail',
     'django.contrib.redirects',
    'compressor',
    'reversion',
    'ckeditor',
    'ckeditor_uploader',

)

MIDDLEWARE_CLASSES = (
    'prozdo_main.middleware.ProzdoUpdateCacheMiddleware',    #cache
    #'django.middleware.gzip.GZipMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'prozdo_main.middleware.ProzdoFetchFromCacheMiddleware',    #cache
)

ROOT_URLCONF = 'prozdo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'prozdo_main/templates/prozdo_main')],
        #'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #'discount.context_processors.debug',
            ],
        },
    },
]

WSGI_APPLICATION = 'prozdo.wsgi.application'





# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'  # URL для медии в шаблонах
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



#SESSION_SAVE_EVERY_REQUEST = True

#**************<<<<<
POST_COMMENTS_PAGE_SIZE = 30
POST_LIST_PAGE_SIZE = 48

#DRUG_THUMB_SETTINGS = {'thumb110': (110, 400), 'thumb220': (220, 800)}
#BLOG_THUMB_SETTINGS = {'thumb110': (110, 400), 'thumb220': (220, 800)}
#COSMETICS_THUMB_SETTINGS = {'thumb110': (110, 400), 'thumb220': (220, 800)}
#USER_PROFILE_THUMB_SETTINGS = {'thumb100': (100, 100)}


BAD_WORDS = (
          '<',
        '>',
        'www',
        'http',
        'href',
        'icq',
        'skype',
        'mail',
        'телефон',
        '@',
        'бля',
        'хуй',
        'хуя',
        'чмо',
        'мудак',
        'гандон',
        'трахн',
        'ебать',
        'ебал',
        'оттрах',
        'стояк',
        'ебок',
        'прода',
        'куплю',
        'руб.',
        'рублей',
        'рубля',
        '00',
       )



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


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'prozdo_main.backends.ProzdoMemcachedCacheCacheBackend',
        'LOCATION': '127.0.0.1:11211',
    }
}

THUMBNAIL_BACKEND = 'prozdo_main.backends.SEOThumbnailBackend'
THUMBNAIL_PREFIX = 'images/'


#COMPRESS_ENABLED = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

BEST_COMMENTS_DAYS = 100

CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"

PROZDO_CACHE_ENABLED = True
PROZDO_CACHE_DURATION = 60 * 60
PROZDO_FULL_PAGE_CACHE_DURATION = PROZDO_CACHE_DURATION
#PROZDO_CACHED_PROPERTY_DURATION = 60 * 60 * 24 * 7
PROZDO_CACHED_ATTRIBUTE_DURATION = 60 * 60 * 24 * 7 * 30
HISTORY_EXISTS_DURATION = 60 * 60 * 24 * 7


DEBUG_TOOLBAR = False


if DEBUG_TOOLBAR:

    DEBUG = True

    TEMPLATE_DEBUG = False

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

    INTERNAL_IPS = ['127.0.0.1']

    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES




if PROZDO_CACHE_ENABLED:

    TEMPLATES[0]['OPTIONS']['loaders'] = [
            ('django.template.loaders.cached.Loader',
                  [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
            ],
                ),
        ]
else:
       TEMPLATES[0]['OPTIONS']['loaders'] = [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
        ]