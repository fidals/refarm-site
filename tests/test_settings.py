import os
import tests

DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'fake-key'

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
                'ecommerce.context_processors.cart',
                'django.contrib.messages.context_processors.messages',
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
    'generic_admin',
    'tests',
)

test_models = {
    'catalog': 'TestCategory',
    'product': 'TestProduct',
    'catalog_with_default_page': 'TestCategoryWithDefaultPage',
}

SEARCH_SEE_ALL_LABEL = 'See all results'

ENTITY_MODEL = 'tests.TestEntity'
ENTITY_MODEL_WITH_SYNC = 'tests.TestEntityWithSync'

# <--- transitive depends on pages app
SITE_ID = 1
SITE_DOMAIN_NAME = 'www.shopelectro.ru'
# ---->

# Settings for eCommerce app.
CART_ID = 'cart'
FAKE_ORDER_NUMBER = 777
PRODUCT_MODEL = 'tests.TestProduct'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SHOP_EMAIL = 'test@test.test'
EMAIL_RECIPIENT = 'test@test.test'
EMAIL_SENDER = 'test@test.test'

