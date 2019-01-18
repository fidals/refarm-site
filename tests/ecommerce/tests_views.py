"""
Tests for views in eCommerce app.
"""

from unittest.mock import patch

from django.apps.registry import apps
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from ecommerce.cart import Cart
from ecommerce.models import Order
from pages.models import CustomPage
from tests.ecommerce.models import MockEcommerceProduct, MockEcommerceCategory


def get_json_carts(response):
    """Get rendered cart's templates from JsonResponse."""
    return response.json()['header'], response.json()['table']


class Cart_(TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test models, get urls for tests."""
        super().setUpClass()
        cls.model = MockEcommerceProduct
        category = MockEcommerceCategory.objects.create(name='Category')
        cls.product1, _ = cls.model.objects.get_or_create(
            name='Product one', price=10, category=category)
        cls.product2, _ = cls.model.objects.get_or_create(
            name='Product two', price=20, category=category)
        cls.add_to_cart = reverse('cart_add')
        cls.remove_from_cart = reverse('cart_remove')
        cls.flush_cart = reverse('cart_flush')
        cls.change_in_cart = reverse('cart_set_count')
        cls.order_page = CustomPage.objects.create(h1='Order page', slug='order')
        cls.patched_model = patch.object(apps, 'get_model', return_value=cls.model)

    def setUp(self):
        """Instantiate a fresh cart for every test case."""
        self.cart = Cart(self.client.session)

    def test_add_to_cart_modifier(self):
        """
        'Add to cart' view should return JsonResponse with rendered header cart and order table
        containing added product.
        """
        with self.patched_model:
            response = self.client.post(
                self.add_to_cart, {'quantity': 1, 'product': self.product1.id},
            )

            header_cart, order_table = get_json_carts(response)

            self.assertIn('In cart: 1', header_cart)
            self.assertIn('Total price: {}'.format(self.product1.price), header_cart)
            self.assertIn(self.product1.name, order_table)

    def test_remove_from_cart_modifier(self):
        """
        'Remove from cart' view should return JsonResponse with rendered header cart and order table
        without removed product.
        """
        self.client.post(
            self.add_to_cart,
            {'quantity': 1, 'product': self.product1.id}
        )
        self.client.post(
            self.add_to_cart,
            {'quantity': 2, 'product': self.product2.id}
        )
        response = self.client.post(
            self.remove_from_cart,
            {'product': self.product1.id}
        )
        header_cart, order_table = get_json_carts(response)
        self.assertIn('In cart: 2', header_cart)
        self.assertIn(self.product2.name, order_table)
        response = self.client.post(
            self.remove_from_cart,
            {'product': self.product2.id}
        )
        header_cart, order_table = get_json_carts(response)
        self.assertIn('The cart is empty', header_cart)
        self.assertNotIn(self.product2.name, order_table)

    def test_flush_cart_modifier(self):
        """'Flush cart' view should return JsonResponse with empty header cart and order table."""
        self.client.post(self.add_to_cart, {'quantity': 1, 'product': self.product1.id})

        response = self.client.post(self.flush_cart)
        header_cart, order_table = get_json_carts(response)

        self.assertIn('The cart is empty', header_cart)
        self.assertNotIn(self.product1.name, order_table)

    def test_change_cart_modifier(self):
        """
        'Change in cart' view should return JsonResponse with header cart and order table
        with changed quantity of a specific product.
        """
        self.client.post(self.add_to_cart, {'quantity': 1, 'product': self.product1.id})

        response = self.client.post(
            self.change_in_cart, {'quantity': 42, 'product': self.product1.id})
        header_cart, order_table = get_json_carts(response)

        self.assertIn('In cart: 42', header_cart)
        self.assertIn(self.product1.name, order_table)

    def test_order_page_with_empty_cart(self):
        """Order page should be empty when the cart is empty."""
        response = self.client.get(self.order_page.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Positions in cart: 0')

    def test_non_empty_cart_after_buy(self):
        """After some shopping we proceed to the order page and should see our cart."""
        self.client.post(self.add_to_cart, {'quantity': 1, 'product': self.product1.id})
        self.client.post(self.add_to_cart, {'quantity': 2, 'product': self.product2.id})

        response = self.client.get(self.order_page.url)

        self.assertContains(response, 'Positions in cart: 2')
        self.assertContains(
            response, 'Total cost: {}'.format(self.product1.price + 2 * self.product2.price))


class Order_(TestCase):

    EMAIL = 'test@example.com'
    PHONE = '+7 (222) 222 22 22'

    def setUp(self):
        self.page = CustomPage.objects.create(slug='order')
        self.success_page = CustomPage.objects.create(slug='order-success')

    @property
    def url(self):
        return reverse(CustomPage.ROUTE, kwargs={'page': 'order'})

    def prepare_cart(self):
        category = MockEcommerceCategory.objects.create(name='Category')
        product = MockEcommerceProduct.objects.create(
            name='Product one', price=10, category=category
        )
        self.client.post(
            reverse('cart_add'), {'quantity': 1, 'product': product.id},
        )

    def place_order(self, email='', phone='') -> None:
        """Do order. Requires prepared cart."""
        email = email or self.EMAIL
        phone = phone or self.PHONE
        response = self.client.post(self.url, {'email': email, 'phone': phone})
        self.assertEqual(302, response.status_code)

    def test_save_to_db(self):
        self.prepare_cart()
        self.place_order()
        count = (
            Order.objects
            .filter(email=self.EMAIL, phone=self.PHONE)
            .count()
        )
        self.assertEqual(1, count)

    def test_send_mail(self):
        self.prepare_cart()
        self.place_order()
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn(self.EMAIL, body)
        self.assertIn(self.PHONE, body)

    def test_order_success_page(self):
        """
        Success page should show actual order.

        Test was created because of this bug:
        https://github.com/fidals/shopelectro/issues/678
        """
        # first order placing
        self.prepare_cart()
        self.place_order('first@mail.me')

        # second order placing
        self.prepare_cart()
        response = self.client.post(
            self.url,
            {'email': 'second@mail.me', 'phone': self.PHONE},
            follow=True
        )
        first, last = Order.objects.first(), Order.objects.last()
        self.assertNotContains(response, str(first))
        self.assertContains(response, str(last))
