import os
import tests

import dj_database_url

DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL',
    )
}

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'fake-key'

BASE_URL = 'top-url-for-ecommerce.com'
BASE_DIR = os.path.dirname(tests.__file__)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# We use logo for products without images.
# So, we need all config for static files processing.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
PLACEHOLDER_IMAGE = 'logo.svg'
PLACEHOLDER_ALT = 'Some useful logo'

USE_CELERY = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ecommerce.context_processors.cart',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.redirects',
    'sorl.thumbnail',
    'mptt',
    'images',
    'catalog',
    'ecommerce',
    'pages',
    'search',
    'generic_admin',
    'tests',
)

SEARCH_SEE_ALL_LABEL = 'See all results'

# <--- transitive depends on pages app
SITE_ID = 1
SITE_DOMAIN_NAME = 'www.shopelectro.ru'
# ---->

# Settings for eCommerce app.
CART_ID = 'cart'
FAKE_ORDER_NUMBER = 777  # for seo magic

CUSTOM_PAGES = {
    'index': {'slug': '', 'h1': 'Index page'},
    'search': {'slug': 'search', 'h1': 'Search page'},
    'catalog': {'slug': 'catalog', 'h1': 'Catalog page'},
    'robots': {'slug': 'robots', 'content': 'Robots content with {{ url }}'},
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_RECIPIENTS = ['test@test.test']
EMAIL_SENDER = 'test@test.test'
