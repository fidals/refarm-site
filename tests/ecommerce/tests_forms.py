"""Tests for forms in eCommerce app."""

from django.test import TestCase

from ecommerce.forms import OrderForm

required_fields = {
    'phone': '123456789',
    'email': 'valid@email.ru',
}
invalid_form_email = {
    'email': 'clearly!not_@_email',
    'phone': '123456789'
}
no_phone = {'email': 'sss@sss.sss'}


class TestForm(TestCase):
    """Test suite for forms in eCommerce app."""

    def test_empty_form(self):
        """Empty form shouldn't be valid."""
        form = OrderForm()
        self.assertFalse(form.is_valid())

    def test_filled_form_without_required_field(self):
        """Form is still not valid, if there are some required fields left unfilled."""
        form = OrderForm(data=no_phone)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        """Form is valid, if there all required fields are filled."""
        form = OrderForm(data=required_fields)
        self.assertTrue(form.is_valid())

    def test_from_validation_on_email_field(self):
        """Form should validate user's email if it is filled."""
        form = OrderForm(data=invalid_form_email)
        self.assertFalse(form.is_valid())
