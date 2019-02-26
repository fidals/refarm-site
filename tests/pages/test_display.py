from django.test import TestCase

from pages import display


class TestFields(TestCase):
    fixtures = []

    def test_attribute_error(self):
        # noinspection PyTypeChecker
        page = display.Page({})
        with self.assertRaises(AttributeError):
            _ = page.bad_attr
