from django.conf.urls import url, include

from tests.generic_admin.tests_views import TableEditorAPI


urlpatterns = [
    url(r'^test_table_editor_api/$', TableEditorAPI.as_view(), name='test_table_editor_api'),
]
