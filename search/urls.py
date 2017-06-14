from django.conf.urls import url

from search.views import Autocomplete, AdminAutocomplete

app_name = 'search'

urlpatterns = [
    url(r'^search/autocomplete/$', Autocomplete.as_view(), name='autocomplete'),
    url(r'^search/autocomplete/admin/$', AdminAutocomplete.as_view()),
]
