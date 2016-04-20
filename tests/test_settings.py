import os

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
				  'blog',
				  )
				  
APP_BLOG_PAGE_TYPES = {
    'article': {'name': 'Статьи', 'alias': ''},
    'news': {'name': 'Новости', 'alias': 'news'},
    'navigation': {'name': 'Навигация', 'alias': 'navigation'},
}
