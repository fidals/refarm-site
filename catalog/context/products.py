import typing

from catalog.context.context import ModelContext
from catalog.models import AbstractCategory, Tag


class Products(ModelContext):

    def __init__(self, qs):
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
        qs = self._context.qs()
        # preserv old order_by params to avoid conflict with `distinct` option
        order_fields = uniq(self._order_by_fields + qs.query.order_by)
        return self._context.qs().order_by(order_field)


class ProductsByCategory(Products):

    def __init__(self, context: Products, category: AbstractCategory):
        self._context = context
        self._category = category

    def qs(self):
        return self._context.qs().active().get_category_descendants(self._category)


class ProductsByTags(Products):

    def __init__(
        self,
        context: Products,
        tags: Tag,
        distinct_fields=None: typing.List['str']
    ):
        self._context = context
        self._tags = tags
        self._distinct_fields = distinct_fields or ['id']

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
