from django.conf.urls import url

from search.views import AutocompleteView, AdminAutocompleteView

app_name = 'search'

# this view classes contain only empty results
urlpatterns = [
    url(r'^search/autocomplete/$', AutocompleteView.as_view(), name='autocomplete'),
    url(r'^search/autocomplete/admin/$', AdminAutocompleteView.as_view()),
]
