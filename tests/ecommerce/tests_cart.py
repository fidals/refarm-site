"""Tests for Cart module."""

from random import randint

from django.test import TestCase

from ecommerce.cart import Cart
from tests.ecommerce.models import EcommerceTestProduct, EcommerceTestCategory


def random_quantity(a=1, b=100):
    return randint(a, b)


class CartTest(TestCase):
    """Test suite for Cart."""

    @property
    def first_product(self):
        """Return first product of class's products list."""
        return self.products[0]

    @property
    def second_product(self):
        """Return second product of class's products list."""
        return self.products[1]

    @classmethod
    def setUpClass(cls):
        """Set up testing models only once."""
        def generate_products(count):
            """Generate Count of products and save it to Products property."""
            category = EcommerceTestCategory.objects.create(
                name='Category for cart tests',
            )
            category.page.slug = 'category-for-cart-tests'
            category.page.save()
            for i in range(1, count + 1):
                product = EcommerceTestProduct.objects.create(
                    name='Product {}'.format(i),
                    price=i * 10,
                    category=category
                )
                yield product

        super(CartTest, cls).setUpClass()
        cls.products = list(generate_products(5))

    def setUp(self):
        """Get session for tests."""
        self.session = self.client.session

    @property
    def cart(self):
        """Return Cart object for tests."""
        return Cart(self.session)

    def test_cart_is_empty(self):
        """Empty Cart in boolean context is False."""
        self.assertFalse(self.cart)

    def test_empty_len(self):
        """Empty cart return 0, when passed to len()."""
        self.assertEqual(len(self.cart), 0)

    def test_empty_total_price(self):
        """Empty cart's total price is 0."""
        self.assertEqual(self.cart.total_price, 0)

    def test_empty_total_count(self):
        """Empty cart's total count is 0."""
        self.assertEqual(self.cart.total_quantity, 0)

    def test_add_to_cart(self):
        """After we add a product to the cart, it should be 'in' Cart."""
        cart = self.cart
        cart.add(self.first_product)
        self.assertTrue(self.first_product.id in cart)

    def test_remove_all_from_cart(self):
        """When we remove the only one product from cart, the cart should be empty."""
        cart = self.cart
        cart.add(self.first_product)
        cart.remove(self.first_product)
        self.assertFalse(cart)

    def test_remove_one_product_from_cart(self):
        """When we remove not all products from cart, products count should be decreased."""
        cart = self.cart
        cart.add(self.first_product)
        cart.add(self.second_product)
        cart.add(self.second_product)
        cart.remove(self.first_product)
        self.assertEqual(cart.total_quantity, 2)

    def test_clear_cart(self):
        """Cart's clear method should remove every product from Cart."""
        cart = self.cart
        cart.add(self.first_product)
        cart.clear()
        self.assertFalse(cart)

    def test_cart_identity(self):
        """Cart constructor should return actual Cart object."""
        self.cart.add(self.first_product)
        self.assertEqual(len(Cart(self.session)), len(self.cart))

    def test_cart_len_after_add(self):
        """Built-in len() function applied to Cart instance should return quantity of positions in Cart."""
        cart = self.cart
        for product in self.products:
            cart.add(product, random_quantity())
        self.assertEqual(len(cart), len(self.products))

    def test_cart_total_price(self):
        """total_price is a sum of prices * quantity for every item in Cart."""
        cart = self.cart
        total_price = 0
        for product in self.products:
            q = random_quantity()
            cart.add(product, q)
            total_price += q * product.price
        self.assertEqual(cart.total_price, total_price)

    def test_cart_total_count(self):
        """total_count is a sum of positions's quantities in Cart."""
        cart = self.cart
        total_quantity = 0
        for product in self.products:
            q = random_quantity()
            total_quantity += q
            cart.add(product, q)
        self.assertEqual(cart.total_quantity, total_quantity)

    def test_cart_generator(self):
        """Since Cart is a generator, we can iterate through its positions."""
        cart = self.cart
        for product in self.products:
            cart.add(product)
        for id_, position in cart:
            self.assertIn(position['name'], [p.name for p in self.products])

    def test_change_quantity_in_cart(self):
        """We can change quantity of existing product in cart."""
        cart = self.cart
        cart.add(self.first_product, 10)
        cart.set_product_quantity(self.first_product, 42)
        self.assertEqual(cart.total_quantity, 42)

    def test_change_quantity_for_nonexistent_product(self):
        """
        If we try to set quantity of product, which not in Cart,
        we will get KeyError.
        """
        cart = self.cart
        cart.add(self.first_product, 10)
        with self.assertRaises(KeyError):
            cart.set_product_quantity(self.second_product, 42)
