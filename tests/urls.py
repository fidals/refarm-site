from django.conf.urls import url, include

from pages import views
from pages.models import Page

from tests.catalog.urls import urlpatterns as catalog_urlpatterns
from tests.pages.urls import urlpatterns as pages_urlpatterns
from tests.ecommerce.urls import urlpatterns as ecommerce_urlpatterns
from tests.generic_admin.urls import urlpatterns as generic_admin_urlpatterns
from tests.search.urls import urlpatterns as search_urlpatterns

app_name = 'tests'


urlpatterns = (
    ecommerce_urlpatterns + generic_admin_urlpatterns + search_urlpatterns +
    catalog_urlpatterns + pages_urlpatterns
)
