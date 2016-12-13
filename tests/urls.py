from django.conf.urls import url, include

from pages import views
from pages.models import Page

from .generic_admin.tests_views import TableEditorAPI

app_name = 'tests'

urlpatterns = [
    url(r'^test_table_editor_api/$', TableEditorAPI.as_view(), name='test_table_editor_api'),
    url(r'^', include('pages.urls')),
    url(r'^(?P<page>)$', views.CustomPageView.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
]

