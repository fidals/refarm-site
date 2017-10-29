"""Tests for models in eCommerce app."""

from django.conf import settings
from django.test import TestCase

from ecommerce.cart import Cart
from ecommerce.models import Order, Position

from tests.ecommerce.models import MockEcommerceProduct, MockEcommerceCategory


class TestModel(TestCase):
    """Test suite for Order and Position models in eCommerce app"""

    @classmethod
    def setUpClass(cls):
        super(TestModel, cls).setUpClass()
        cls.mail = 'nobody@nowhere.net'
        category = MockEcommerceCategory.objects.create(name='Category')
        cls.model = MockEcommerceProduct
        cls.product1, _ = cls.model.objects.get_or_create(
            name='Product one', price=10.1, category=category)
        cls.product2, _ = cls.model.objects.get_or_create(
            name='Product two', price=20.2, category=category)

    def setUp(self):
        """Initialize test data for every test case."""
        super().setUp()
        self.session = self.client.session
        self.cart = Cart(self.client.session)

    def test_create_order(self):
        """We should be able to create Order with every required filed specified."""
        order = Order(email=self.mail)
        order.save()
        self.assertEqual(Order.objects.get(pk=order.id), order)

    def test_set_positions_in_order(self):
        """
        We can set all the positions in cart in Order.

        It will automatically instantiate Position instance for every one.
        """
        self.cart.add(self.product1)
        self.cart.add(self.product2)
        order = Order(email=self.mail)
        order.save()
        order = order.set_positions(self.cart)
        saved_order = Order.objects.get(pk=order.id)
        self.assertEqual(saved_order.positions.count(), 2)

    def test_total_cost_in_order(self):
        """total_price method should return sum of price * count for every product. """
        self.cart.add(self.product1, 10)
        self.cart.add(self.product2, 3)
        order = Order(email=self.mail)
        order.save()
        order = order.set_positions(self.cart)
        self.assertEqual(order.total_price,
                         self.product1.price * 10 + self.product2.price * 3)

    def test_cost_for_item(self):
        """cost should return price of an item multiplied by its count."""
        order = Order(email=self.mail)
        item = Position(
            order=order,
            product_id=self.product1.id,
            name=self.product1.name,
            price=10,
            quantity=30
        )
        self.assertEqual(item.total_price, 10 * 30)

    def test_fake_number_order(self):
        """Order number should be increased by a FAKE_ORDER_NUMBER const"""
        order = Order()
        order.save()
        self.assertGreater(order.fake_order_number, settings.FAKE_ORDER_NUMBER)
