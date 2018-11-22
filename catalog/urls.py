"""
Routes for catalog app.
"""
from django.conf.urls import url

from catalog.views import catalog

app_name = 'catalog'

urlpatterns = [
    url(r'^category/(?P<slug>[\w-]+)/$', catalog.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<slug>[\w-]+)/tags/(?P<tags>[\w_-]+)/$',
        catalog.CategoryPage.as_view(), name='category'),
    url(r'^no-images/$', catalog.ProductsWithoutImages.as_view(), name='products_without_images'),
    url(r'^no-text/$', catalog.ProductsWithoutText.as_view(), name='products_without_text'),
    url(r'^product/(?P<product_id>[0-9]+)/$', catalog.ProductPage.as_view(), name='product'),
]
