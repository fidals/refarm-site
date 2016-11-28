from django.conf.urls import url

from . import views

app_name = 'pages'

urlpatterns = [
    # /one/
    url(r'^([\w-]+)/$', views.FlatPageView.as_view(), name='flat_page'),
    # /one/two/
    url(r'^{}$'.format(r'([\w-]+)/'*2), views.FlatPageView.as_view(), name='flat_page'),
    # /one/two/three/
    url(r'^{}$'.format(r'([\w-]+)/'*3), views.FlatPageView.as_view(), name='flat_page'),
    # /one/two/three/four/
    url(r'^{}$'.format(r'([\w-]+)/'*4), views.FlatPageView.as_view(), name='flat_page'),
]
