from django.conf.urls import url

from tests.search.views import (
    MockAutocompleteView, MockAdminAutocompleteView, MockSearchView
)

from pages.models import Page

urlpatterns = [
    url(
        r'^(?P<page>search)/$',
        MockSearchView.as_view(),
        name=Page.CUSTOM_PAGES_URL_NAME
    ),
    url(
        r'^search/autocomplete/$',
        MockAutocompleteView.as_view(),
        name='mock_autocomplete'
    ),
    url(
        r'^search/autocomplete/admin/$',
        MockAdminAutocompleteView.as_view(),
        name='mock_admin_autocomplete'
    ),
]
