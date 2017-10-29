from django.conf.urls import url, include

from tests.search.views import MockSearchView

from pages.models import Page

urlpatterns = [
    url(r'^(?P<page>search)/$', MockSearchView.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^search/', include('search.urls')),
]
