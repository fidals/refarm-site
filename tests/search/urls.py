from django.conf.urls import url, include

from tests.search.views import TestSearch

from pages.models import Page

urlpatterns = [
    url(r'^(?P<page>search)/$', TestSearch.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^search/', include('search.urls')),
]
