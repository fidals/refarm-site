import typing

from django.db.models import QuerySet

from catalog.context.context import Products, Tags, Category
from catalog.models import AbstractCategory


class ActiveProducts(Products):

    def __init__(self, context: Products):
        self._context = context

    def qs(self):
        return self._context.qs().active()


class OrderedProducts(Products):

    def __init__(self, context: Products, req_kwargs):
        self._context = context
        self._sorting_index = self._req_kwargs.get('sorting', 0)

    def qs(self):
        return self._context.qs().order_by(
            SortingOption(index=self._sorting_index).directed_field,
        )

    def context(self):
        return {
            **super().context(),
            'sorting_index': _sorting_index,
        }


class ProductsByCategory(Products):

    def __init__(self, context: Products, category: AbstractCategory):
        self._context = context
        self._category = category

    def qs(self):
        return self._context.qs().get_category_descendants(self._category)


class ProductsByTags(Products):

    def __init__(self, context: Products, tags_context: Tags):
        self._context = context
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if tags.exists():
            return self._context.qs().tagged(tags)
        else:
            return self._context.qs()
