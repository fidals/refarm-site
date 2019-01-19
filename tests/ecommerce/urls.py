from django.conf.urls import url, include

from ecommerce import views
from pages.urls import custom_page_url
from tests.ecommerce.views import (
    MockAddToCart, MockChangeCount, MockFlushCart, MockRemoveFromCart
)

test_url = [
    url(r'^cart-add/$', MockAddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', MockChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', MockFlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', MockRemoveFromCart.as_view(), name='cart_remove'),
]

urlpatterns = [
    url(r'^catalog/', include('catalog.urls')),
    url(r'^shop/', include(test_url)),
    custom_page_url(r'^shop/(?P<page>order)/$', views.OrderPage.as_view()),
    custom_page_url(r'^shop/(?P<page>order-success)/$', views.OrderSuccess.as_view()),
]
