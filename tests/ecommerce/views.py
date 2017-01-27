from ecommerce.views import AddToCart, RemoveFromCart, ChangeCount, FlushCart
from tests.ecommerce.models import EcommerceTestProduct


class TestAddToCart(AddToCart):
    product_model = EcommerceTestProduct


class TestRemoveFromCart(RemoveFromCart):
    product_model = EcommerceTestProduct


class TestFlushCart(FlushCart):
    product_model = EcommerceTestProduct


class TestChangeCount(ChangeCount):
    product_model = EcommerceTestProduct
