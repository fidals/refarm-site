"""Models for eCommerce app: Order and OrderItem with 1:n relation."""

from django.conf import settings
from django.db import models


class Order(models.Model):
    """
    Order class.
    Information about order: cart, credentials of customer, date added and other.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=255, null=True, blank=True)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        A string representation of Order.
        :return: a string with 'Order #id' format.
        """
        return 'Order #{}'.format(self.id)

    @property
    def fake_order_number(self):
        """Fake order number for SEO magic, so we look cool"""
        return self.id + settings.FAKE_ORDER_NUMBER

    @property
    def total_price(self):
        """
        Sum of positions's prices in Order.

        Note: does not work through QuerySet.aggregate() because
        position.total_price is not model field.
        """
        return sum(position.total_price for position in self.positions.all())

    @property
    def items(self):
        """
        Define items in order as a property.
        A little bit of syntactic sugar :)
        """
        return self.positions.all()

    def set_positions(self, cart):
        """
        Save cart's state into Order instance.

        :param cart: user's cart
        :return: self
        """
        self.save()
        for id_, position in cart:
            self.positions.create(
                order=self,
                product_id=id_,
                name=position['name'],
                price=position['price'],
                quantity=position['quantity']
            )
        return self


class Position(models.Model):
    """
    An item in the order.
    Information about one item in the order: product, price when added, quantity
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='positions', db_index=True
    )
    product_id = models.IntegerField()
    vendor_code = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(max_length=255)
    quantity = models.PositiveSmallIntegerField(default=0)
    price = models.FloatField(blank=True, null=True)

    @property
    def total_price(self):
        return self.price * self.quantity
