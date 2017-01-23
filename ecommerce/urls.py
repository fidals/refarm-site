from django.conf.urls import url

from ecommerce import views

app_name = 'ecommerce'

urlpatterns = [
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
]
