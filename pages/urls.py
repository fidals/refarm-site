from django.conf.urls import url

from . import views

app_name = 'pages'
urlpatterns = [
    url(r'^([\w-]+)/$', views.page, name='page'),
    url(r'^{}$'.format(r'([\w-]+)/'*2), views.page, name='page'),
    url(r'^{}$'.format(r'([\w-]+)/'*3), views.page, name='page'),
    url(r'^{}$'.format(r'([\w-]+)/'*4), views.page, name='page'),
]
