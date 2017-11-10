from django.conf.urls import url, include

from pages.models import Page
from pages.views import CustomPageView

from tests.catalog.views import (
    TestCategoryTree, TestProductPage, TestProductsWithoutImages,
    TestProductsWithoutText
)


urlpatterns = [
    url(r'^no-images/$', TestProductsWithoutImages.as_view(), name='products_without_images'),
    url(r'^no-text/$', TestProductsWithoutText.as_view(), name='products_without_text'),
    url(r'^product/(?P<product_id>[0-9]+)/$', TestProductPage.as_view(), name='product'),
    url(r'^(?P<page>)/$', CustomPageView.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^(?P<page>catalog)/$', TestCategoryTree.as_view(), name=Page.CUSTOM_PAGES_URL_NAME),
    url(r'^catalog/', include('catalog.urls')),
]
