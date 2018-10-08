import typing

from django.db.models import QuerySet

from catalog.context.context import ModelContext
from catalog.models import AbstractCategory


class Products(ModelContext):

    def __init__(self, qs: QuerySet):
        self._qs = qs

    def qs(self):
        return self._qs

    def context(self):
        return {
            'products': self.qs(),
        }


class ActiveProducts(Products):

    def __init__(self, context: Products):
        self._context = context

    def qs(self):
        return self._context.qs().active()


class OrderedProducts(Products):

    def __init__(self, context: Products, order_by_fields: typing.List[str]):
        self._context = context
        self._order_by_fields = order_by_fields

    def qs(self):
        return self._context.qs().order_by(self._order_by_fields)


class ProductsByCategory(Products):

    def __init__(self, context: Products, category: AbstractCategory):
        self._context = context
        self._category = category

    def qs(self):
        return self._context.qs().active().get_category_descendants(self._category)


class ProductsByTags(Products):

    def __init__(self, context: Products, tags: QuerySet):
        self._context = context
        self._tags = tags

    def qs(self):
        qs = self._context.qs()
        # Distinct because a relation of tags and products is M2M.
        # We do not specify the args for `distinct` to avoid dependencies
        # between `order_by` and `distinct` methods.

        # Postgres has `SELECT DISTINCT ON`, that depends on `ORDER BY`.
        # See docs for details:
        # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-DISTINCT
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        return qs.filter(tags__in=self._tags).distinct()
