import os
from . import config_factory

DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'pages.urls'

SECRET_KEY = 'fake-key'

INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  'pages',
                  )

APP_BLOG_POST_TYPES = config_factory.get_usual()

CRUMBS = {
    'main': 'Main',
    'pages': 'Posts list',
}
