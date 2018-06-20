from functools import partial

from django.conf.urls import url, include

from pages import views
from pages.models import Page

# @todo #343:30m Use custom_page_url for custom page routes.
custom_page_url = partial(url, name=Page.CUSTOM_PAGES_URL_NAME)


urlpatterns = [
    url(r'^', include('pages.urls')),
    custom_page_url(r'^(?P<page>)$', views.CustomPageView.as_view()),
    custom_page_url(r'^(?P<page>robots)$', views.RobotsView.as_view(is_db=True)),
    url(r'^robots-t$', views.RobotsView.as_view(template='robots.txt'), name='robots-template'),
]
