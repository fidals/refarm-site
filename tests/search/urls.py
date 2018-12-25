from django.conf.urls import url

from tests.search.views import (
    MockAutocompleteView, MockAdminAutocompleteView, MockSearchView
)

from pages.models import CustomPage

urlpatterns = [
    url(
        r'^(?P<page>search)/$',
        MockSearchView.as_view(),
        name=CustomPage.ROUTE
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
