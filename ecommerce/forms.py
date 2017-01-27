from django import forms

from ecommerce.models import Order


class OrderForm(forms.ModelForm):
    """
    Form for making order. Based on Order model.
    Define required contact information about a customer.
    """
    class Meta:
        model = Order
        fields = ['name', 'email', 'phone', 'city']


class OrderBackcallForm(forms.Form):
    """Form for making Backcall order."""

    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
