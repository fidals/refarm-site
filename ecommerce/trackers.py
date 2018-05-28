"""
@todo #292 Implement YaEcommerceTracker and GAEcommerceTracker classes.
"""
import abc


class EcommerceTracker(abc.ABC):

    def __init__(self, name):
        self.name = name
        self.data = []


class Trackers:

    def __init__(self, trackers):
        self.trackers = trackers

    def __iter__(self):
        for tracker in self.trackers:
            yield tracker

    def add(self, product, quantity):
        for tracker in self.trackers:
            tracker.add(product, quantity)

    def remove(self, product):
        for tracker in self.trackers:
            tracker.remove(product)

    def clear(self, cart):
        for tracker in self.trackers:
            tracker.clear(cart)

    def purchase(self, order):
        for tracker in self.trackers:
            tracker.purchase(order)


class YaEcommerceTracker(EcommerceTracker):
    """
    Prepare a data of user's actions for yandex ecommerce analitics.

    Yandex requires the synchronization of data after any successful action,
    so it should be used after changing a state.

    docs: https://yandex.ru/support/metrika/data/e-commerce.html
    """

    def add(self, product):
        pass

    def remove(self, product):
        pass

    def clear(self, product):
        pass

    def purchase(self, order):
        pass


class GAEcommerceTracker(EcommerceTracker):
    """
    Prepare a data of user's actions for google ecommerce analitics.

    Google requires the synchronization of data after a successful purchase.

    docs: https://developers.google.com/analytics/devguides/collection/analyticsjs/ecommerce
    """

    def add(self, product):
        pass

    def remove(self, product):
        pass

    def clear(self, product):
        pass

    def purchase(self, order):
        pass
