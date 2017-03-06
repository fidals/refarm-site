from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def humanize_price(price):
    return intcomma(floatformat(price, 0))
