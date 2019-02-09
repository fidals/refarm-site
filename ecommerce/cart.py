from copy import deepcopy

from django.conf import settings
from django.db.models import Model

from images.templatetags.images import placeholder_image_url


class Cart:
    """
    Cart class. An abstraction over the session's 'cart'-key object.

    Cart inner data structure looks like this:
    cart = {
        123: {  # models.Product.id
            500.00,  # models.Product.price (float)
            2,  # quantity in cart of positions with id=123
            'Battery MR720',  # models.Product.name
        }
    }
    """

    REQUIRED_POSITION_FIELDS = ['id', 'name', 'price']

    def __init__(self, session):
        """
        Save user's session in object property.
        If there is no Cart in session - instantiates it.
        """
        self._session = session
        cart = self._session.get(settings.CART_ID)

        if not cart:
            cart = self._session[settings.CART_ID] = {}

        self._cart = Cart.deserialize(cart)

    @staticmethod
    def deserialize(session_cart):
        """Translate Cart object from session format to Cart object format."""
        return {int(k): v for k, v in session_cart.items()}

    def __iter__(self):
        """
        Iterate over the positions in the Cart,
        add 'position' key with respective model to every item.
        """
        # Since dict is mutable we should copy it.
        cart = deepcopy(self._cart)

        # without cart.values() sorting because json serializing for front mixes dict
        for id_, item in cart.items():
            item['total_price'] = item['quantity'] * item['price']
            yield id_, item

    def __len__(self):
        """Return number of positions in Cart."""
        return len(self._cart)

    def __bool__(self):
        """True if Cart has at least one item, False otherwise."""
        return bool(self._cart)

    def __contains__(self, position_id):
        """Return True if given position in Cart, False otherwise."""
        return position_id in self._cart

    def save(self):
        """Actualize cart in session and trigger 'modified' event on it."""
        self._session[settings.CART_ID] = self._cart
        self._session.modified = True  # Tells Django that session must be saved

    def update_position_prices(self, new_positions):
        """Update position price in cart."""
        for item in new_positions:
            self._cart[item['id']]['price'] = item['price']
        self.save()

    def get_position_data(self, position):
        page = getattr(position, 'page', None)
        image_path = (
            page.main_image.url
            if (page and page.main_image) else placeholder_image_url()
        )
        return {
            'name': position.name,
            'price': position.price if position.price else 0,
            'in_stock': position.in_stock,
            'image': image_path,
            'url': position.url,
        }

    def add(self, position: Model, quantity=1):
        """Add a Position to the Cart or update its quantity if it's already in it."""
        for field in self.REQUIRED_POSITION_FIELDS:
            assert hasattr(position, field), f'Position has not required field "{field}"'

        if position.id not in self:
            self._cart[position.id] = self.get_position_data(position)
            self._cart[position.id]['quantity'] = quantity
        else:
            self._cart[position.id]['quantity'] += quantity
        self.save()

    def set_position_quantity(self, position: Model, quantity: int):
        """Change quantity of a Position in Cart. Raise IndexError if Position not in Cart."""
        self._cart[position.id]['quantity'] = quantity
        self.save()

    def remove(self, position: Model):
        """Remove a position from the cart."""
        if position.id in self._cart:
            del self._cart[position.id]
            self.save()

    @property
    def total_price(self):
        """Count total price in cart."""
        return sum(item['total_price'] for _, item in self)

    @property
    def total_quantity(self):
        """Total quantity of positions in cart."""
        return sum(item['quantity'] for _, item in self)

    def clear(self):
        """Clear cart object from session."""
        del self._session[settings.CART_ID]
        self._cart = {}

    def is_empty(self):
        return not bool(self._cart)
