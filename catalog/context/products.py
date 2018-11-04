import typing

from django.db.models import QuerySet

from catalog.context.context import Products, Tags
from catalog.models import AbstractCategory


class ActiveProducts(Products):

    def __init__(self, products: Products):
        self._products = products

    def qs(self):
        return self._products.qs().active()


class OrderedProducts(Products):

    def __init__(self, products: Products, req_kwargs):
        self._products = products
        self._sorting_index = self._req_kwargs.get('sorting', 0)

    def qs(self):
        return self._products.qs().order_by(
            SortingOption(index=self._sorting_index).directed_field,
        )

    def context(self):
        return {
            **super().context(),
            'sorting_index': self._sorting_index,
        }


class ProductsByCategory(Products):

    def __init__(self, products: Products, category: AbstractCategory):
        self._products = products
        self._category = category

    def qs(self):
        return self._products.qs().get_category_descendants(self._category)


class ProductsByTags(Products):

    def __init__(self, products: Products, tags_context: Tags):
        self._products = products
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if tags.exists():
            return self._products.qs().tagged(tags)
        else:
            return self._products.qs()
