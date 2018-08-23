import unittest

from django.db import models
from django.core.urlresolvers import reverse
from django.test import TestCase

from catalog.models import AbstractCategory, AbstractProduct, Tag, TagGroup

from pages.models import SyncPageMixin, CustomPage


class MockCategory(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug,))


class MockCategoryWithDefaultPage(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug, ))


class MockProduct(AbstractProduct, SyncPageMixin):
    category = models.ForeignKey(
        MockCategory, on_delete=models.CASCADE,
        default=None, related_name='products',
        db_index=True
    )

    def get_absolute_url(self):
        return reverse('product', args=(self.id, ))

    @property
    def image(self):
        return 'no-image-right-now'


class TagTest(TestCase):

    # @todo #162:60m Create fixtures for tags.
    #  Copy from SE all tags fixtures creation logic.
    #  Resurrect tags test.

    @unittest.skip
    def test_double_named_tag_saving(self):
        """Two tags with the same name should have unique slugs."""
        def save_doubled_tag(tag_from_):
            group_to = TagGroup.objects.exclude(id=tag_from_.group.id).first()
            tag_to_ = Tag(
                group=group_to, name=tag_from_.name, position=tag_from_.position
            )
            # required to create `tag.products` field
            tag_to_.save()
            tag_to_.products.set(tag_from.products.all())
            tag_to_.save()
            return tag_to_
        tag_from = Tag.objects.first()
        tag_to = save_doubled_tag(tag_from)
        self.assertNotEqual(tag_from.slug, tag_to.slug)
