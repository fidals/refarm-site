"""
Routes for catalog app.
"""
from django.conf.urls import url

from catalog.views import search, catalog

app_name = 'catalog'

urlpatterns = [
    url(r'^category/(?P<slug>[\w-]+)/$', catalog.CategoryPage.as_view(), name='category'),
    url(r'^no-images/$', catalog.ProductsWithoutImages.as_view(), name='products_without_images'),
    url(r'^no-text/$', catalog.ProductsWithoutText.as_view(), name='products_without_text'),
    url(r'^product/(?P<product_id>[0-9]+)/$', catalog.ProductPage.as_view(), name='product'),
    url(r'^search/autocomplete/$', search.Autocomplete.as_view(), name='autocomplete'),
    url(r'^search/autocomplete/admin/$', search.AdminAutocomplete.as_view()),
]
