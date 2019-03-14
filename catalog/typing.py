from django.db.models import QuerySet

from catalog.models import ProductQuerySet
from pages.typing import *

QuerySet = Union[QuerySet, Iterable]
Products = Union[ProductQuerySet, Iterable]
