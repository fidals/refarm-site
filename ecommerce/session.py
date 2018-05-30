class ShoppingSession:
    """
    Shopping session of user.

    Session has ability to updating a state of the cart and signal about to
    ecommerce analytics.
    """

    def __init__(self, cart, trackers):
        self.cart = cart
        self.trackers = trackers

    def add(self, product, quantity=1):
        self.cart.add(product, quantity)
        self.trackers.add(product, quantity)

    def set_product_quantity(self, product, quantity: int):
        self.cart.set_product_quantity(product, quantity)
        self.trackers.remove(product)
        self.trackers.add(product, quantity)

    def remove(self, product):
        self.cart.remove(product)
        self.trackers.remove(product)

    def clear(self):
        self.cart.clear()
        self.trackers.clear(self.cart)

    def purchase(self, order):
        self.trackers.purchase(order)
        self.cart.clear()

    def get_tracked_data(self):
        return {
            tracker.name: tracker.data for tracker in self.trackers
        }
