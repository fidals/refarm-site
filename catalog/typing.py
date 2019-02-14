from typing import *

from catalog.models import ProductQuerySet

from django.db.models import QuerySet

QuerySet = Union[QuerySet, Iterable]
Products = Union[ProductQuerySet, Iterable]
