from ecommerce.views import AddToCart, RemoveFromCart, ChangeCount, FlushCart
from tests.ecommerce.models import MockEcommerceProduct


class MockAddToCart(AddToCart):
    position_model = MockEcommerceProduct


class MockRemoveFromCart(RemoveFromCart):
    position_model = MockEcommerceProduct


class MockFlushCart(FlushCart):
    position_model = MockEcommerceProduct


class MockChangeCount(ChangeCount):
    position_model = MockEcommerceProduct
