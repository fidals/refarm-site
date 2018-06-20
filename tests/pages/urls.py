from django.conf.urls import url, include

from pages import views
from pages.models import Page

urlpatterns = [
    url(r'^', include('pages.urls')),
    url(r'^(?P<page>)$', views.CustomPageView.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^(?P<page>robots)$', views.RobotsView.as_view(is_db=True), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^robots-t$', views.RobotsView.as_view(template='robots.txt'), name='robots-template'),
]
