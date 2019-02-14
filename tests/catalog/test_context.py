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
    PER_PAGE = 30

    def test_paginated_qs(self):
        left_qs, right_qs = 2 * (catalog_models.MockProduct.objects.all(), )
        with override_settings(CATEGORY_STEP_MULTIPLIERS=[self.PER_PAGE]):
            self.assertEqual(
                list(left_qs[:self.PER_PAGE]),
                list(context.products.PaginatedProducts(
                    right_qs, '', 1, self.PER_PAGE,
                ).products),
            )

    def test_paginated_404(self):
        page_number = 1
        with override_settings(CATEGORY_STEP_MULTIPLIERS=[self.PER_PAGE]):
            with self.assertRaises(Http404):
                # per_page not in CATEGORY_STEP_MULTIPLIERS
                context.products.PaginatedProducts(None, '', page_number, self.PER_PAGE - 1)

            with self.assertRaises(Http404):
                # page number doesn't exist
                context.products.PaginatedProducts(None, '', page_number - 1, self.PER_PAGE)


class TagsContext(TestCase):

    def test_parsed_tags(self):
        tags_ctx = mocked_ctx()
        context.tags.ParsedTags(tags_ctx, raw_tags='test1=test2').qs()
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
