"""
@todo #213:30m Remove mocked Context classes.
 Wait for fixtures of Tag models to implement this.
"""

import unittest

from django.test import TestCase, override_settings
from django.http import Http404

from catalog import newcontext as context
from tests.catalog import models as catalog_models


def mocked_ctx(qs_attrs=None, context_attrs=None):
    ctx = unittest.mock.Mock()
    ctx.qs.return_value = unittest.mock.Mock(**(qs_attrs or {}))
    ctx.context.return_value = unittest.mock.Mock(**(context_attrs or {}))

    return ctx


class ProductsContext(TestCase):

    fixtures = ['catalog.json']

    def products_ctx(self, qs=None) -> context.context.Products:
        return context.context.Products(qs or catalog_models.MockProduct.objects.all())

    def test_ordered_products(self):
        order_by = 'price'
        with override_settings(CATEGORY_SORTING_OPTIONS={
            1: {'label': order_by, 'field': order_by, 'direction': ''}
        }):
            products_ctx = self.products_ctx()
            self.assertEqual(
                list(products_ctx.qs().order_by(order_by)),
                list(context.products.OrderedProducts(products_ctx, 1).qs()),
            )

    def test_paginated_qs(self):
        with override_settings(CATEGORY_STEP_MULTIPLIERS=[30]):
            products = self.products_ctx()
            per_page = 30
            self.assertEqual(
                list(products.qs()[:per_page]),
                list(context.products.PaginatedProducts(
                    products, '', 1, per_page,
                ).qs()),
            )

    def test_paginated_404(self):
        per_page = 30
        page_number = 1
        with override_settings(CATEGORY_STEP_MULTIPLIERS=[per_page]):
            with self.assertRaises(Http404):
                # per_page not in CATEGORY_STEP_MULTIPLIERS
                context.products.PaginatedProducts(None, '', page_number, per_page-1)

            with self.assertRaises(Http404):
                # page_number < 1
                context.products.PaginatedProducts(None, '', page_number-1, per_page)

    def test_tagged_products(self):
        products_ctx = mocked_ctx()
        context.products.TaggedProducts(
            products_ctx, mocked_ctx(qs_attrs={'exists.return_value': True}),
        ).qs()

        self.assertTrue(products_ctx.qs().tagged.called)

    def test_non_tagged_products(self):
        """If there are no tags, then products don't changed."""
        products_ctx = mocked_ctx()
        context.products.TaggedProducts(
            products_ctx, mocked_ctx(qs_attrs={'exists.return_value': False}),
        ).qs()

        self.assertFalse(products_ctx.qs().tagged.called)


class TagsContext(TestCase):

    def test_parsed_tags(self):
        tags_ctx = mocked_ctx()
        context.tags.ParsedTags(tags_ctx, 'test').qs()
        self.assertTrue(tags_ctx.qs().parsed.called)

    def test_unparsed_tags(self):
        self.assertFalse(
            context.tags.ParsedTags(
                mocked_ctx(qs_attrs={'none.return_value': []}), '',
            ).qs()
        )

    def test_404_check_tags(self):
        with self.assertRaises(Http404):
            context.tags.Checked404Tags(mocked_ctx(qs_attrs={'exists.return_value': False})).qs()
