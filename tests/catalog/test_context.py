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

    @override_settings(CATEGORY_SORTING_OPTIONS={
        1: {'label': 'price', 'field': 'price', 'direction': ''}
    })
    def test_ordered_products(self):
        products_ctx = mocked_ctx()
        context.products.OrderedProducts(products_ctx, {'sorting': 1}).qs()
        self.assertTrue(products_ctx.qs().order_by.called)
        self.assertEqual(products_ctx.qs().order_by.call_args[0][0], 'price')

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
        raw_tags = 'test'
        context.tags.ParsedTags(tags_ctx, {'tags': raw_tags}).qs()
        self.assertTrue(tags_ctx.qs().parsed.called)

    def test_unparsed_tags(self):
        tags_ctx = mocked_ctx()
        context.tags.ParsedTags(tags_ctx, {}).qs()
        self.assertFalse(tags_ctx.qs().parsed.called)

    def test_404_check_tags(self):
        with self.assertRaises(Http404):
            context.tags.Checked404Tags(mocked_ctx(qs_attrs={'exists.return_value': False})).qs()
