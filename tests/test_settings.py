import os
import tests

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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'sorl.thumbnail',
    'images',
    'pages',
    'tests',
)

ENTITY_MODEL = 'tests.TestEntity'
ENTITY_MODEL_WITH_SYNC = 'tests.TestEntityWithSync'

# <--- transitive depends on pages app
PRODUCTS_TO_LOAD = 30
SITE_ID = 1
SITE_DOMAIN_NAME = 'www.shopelectro.ru'
# ---->
