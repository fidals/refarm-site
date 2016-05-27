import os
from . import config_factory

DIRNAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

ROOT_URLCONF = 'blog.urls'

SECRET_KEY = 'fake-key'

INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  'seo',
                  'blog',
                  )

APP_BLOG_POST_TYPES = config_factory.get_usual()

CRUMBS = {
    'main': 'Main',
    'blog': 'Posts list',
}
