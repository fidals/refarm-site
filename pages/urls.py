from functools import partial

from django.conf.urls import url

from pages import views
from pages.models import Page

app_name = 'pages'

# @todo #343:30m Use custom_page_url for every custom page route.
custom_page_url = partial(url, name=Page.CUSTOM_PAGES_URL_NAME)

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
