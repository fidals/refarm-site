from ecommerce.views import AddToCart, RemoveFromCart, ChangeCount, FlushCart
from tests.ecommerce.models import MockEcommerceProduct


class MockAddToCart(AddToCart):
    product_model = MockEcommerceProduct


class MockRemoveFromCart(RemoveFromCart):
    product_model = MockEcommerceProduct


class MockFlushCart(FlushCart):
    product_model = MockEcommerceProduct


class MockChangeCount(ChangeCount):
    product_model = MockEcommerceProduct
