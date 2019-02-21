"""Defines tests for models in Catalog app."""
import unittest
from random import shuffle

from django.db import DataError
from django.test import TestCase

import catalog
from pages.models import CustomPage
from tests.catalog import models as catalog_models


class TestCategoryTree(TestCase):
    """Test suite for category operations"""

    def setUp(self):
        """
        Defines testing data.
        Two categories: Root and Child (of root).
        Two products: popular and unpopular (both from Child category)
        """

        self.test_root_category = catalog_models.MockCategory.objects.get_or_create(
            name='Test root'
        )[0]

        self.test_child_of_root_category = catalog_models.MockCategory.objects.get_or_create(
            name='Test child',
            parent=self.test_root_category
        )[0]

        self.test_child_of_ancestor_category = catalog_models.MockCategory.objects.get_or_create(
            name='Test descendants',
            parent=self.test_child_of_root_category
        )[0]

        self.test_unpopular_product = catalog_models.MockProduct.objects.get_or_create(
            name='Unpopular',
            price=10,
            category=self.test_child_of_root_category,
            in_stock=10
        )[0]

        self.test_popular_product = catalog_models.MockProduct.objects.get_or_create(
            name='Popular',
            price=20,
            category=self.test_child_of_ancestor_category,
            in_stock=10,
            is_popular=True,
        )[0]

    def test_root_categories(self):
        """There should be only one root category."""

        roots = catalog_models.MockCategory.objects.root_nodes()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].name, self.test_root_category.name)

    def test_children_of_root(self):
        """Should be one direct child of root category."""

        roots = catalog_models.MockCategory.objects.root_nodes()[0]
        children = roots.get_children()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].name, self.test_child_of_root_category.name)

    def test_root_has_no_products(self):
        """Root category shouldn't have any products."""

        roots = catalog_models.MockCategory.objects.root_nodes()[0]
        products = roots.products.all()
        self.assertFalse(products.exists())


class CategoryToPageRelationTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_tree_page, _ = CustomPage.objects.get_or_create(slug='catalog')
        cls.root_category = catalog_models.MockCategoryWithDefaultPage.objects.create(
            name='All batteries',
        )
        cls.root_category.page.slug = 'all'
        cls.root_category.page.save()
        cls.page_type = cls.root_category.related_model_name

    def __create_category(self, slug, page=None):
        category = catalog_models.MockCategoryWithDefaultPage.objects.create(
            name='Battery {}'.format(slug),
            page=page,
            parent=self.root_category
        )
        category.page.slug = slug
        category.page.save()
        return category

    def test_category_create_related_page(self):
        """
        MockCategoryWithDefaultPage without related page should create and return related page
        by MockCategoryWithDefaultPage.save() call
        """
        category = self.__create_category(slug='first')
        self.assertTrue('category' in category.page.related_model_name)
        self.assertEqual(category.url, category.page.url)
        self.assertEqual(category.page.model, category)

    def test_category_tree_page_parent(self):
        """
        MockCategoryWithDefaultPage tree page should be auto-created as page parent
        for every root MockCategoryWithDefaultPage. In other words:
        MockCategoryWithDefaultPage.page.parent == category_tree_page
        """
        slug = 'fifth'
        category = catalog_models.MockCategoryWithDefaultPage.objects.create(
            name='Battery {}'.format(slug), parent=None)
        category.page.slug = slug
        category.page.save()
        self.assertEqual(category.page.parent, self.category_tree_page)

    def test_category_create_page_for_sync_tree(self):
        """
        MockCategoryWithDefaultPage should bind parent for it's page if parent doesn't exist
        """
        category = self.__create_category(slug='sixth')
        self.assertEqual(category.parent.page, category.page.parent)
        self.assertEqual(category.parent.page.slug, category.page.parent.slug)

    def test_category_return_page_by_sync_tree(self):
        """
        If MockCategoryWithDefaultPage page have parent,
        MockCategoryWithDefaultPage save() hook should do nothing
        """
        category = self.__create_category(slug='seventh')
        category.page.parent = self.root_category.page
        category.page.save()
        category.save()  # category.save() hooks sync_tree() method
        self.assertEqual(category.page.parent, self.root_category.page)


class TestProductToPageRelation(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root_category = catalog_models.MockCategory.objects.create(
            name='All batteries',
        )
        cls.root_category.page.slug = 'all'
        cls.root_category.page.save()
        cls.page_type = 'catalog_product'

    @classmethod
    def create_product(self, slug, page=None):
        return catalog_models.MockProduct.objects.create(
            name=slug,
            page=page,
            category=self.root_category,
            price=123
        )

    @property
    def category_tree_page(self):
        return CustomPage.objects.get(slug='category_tree')

    def test_product_create_related_page(self):
        """
        MockProduct without related page should create and return related page
        by product.save() call
        """
        product = self.create_product(slug='first')
        self.assertEqual(product.related_model_name, product.page.related_model_name)
        self.assertTrue(product.page.model, product)

    def test_category_create_page_for_sync_tree(self):
        """
        MockProduct should bind parent for it's page if parent doesn't exist
        """
        product = self.create_product(slug='sixth')
        category = product.category
        self.assertEqual(category, product.parent)
        self.assertEqual(category.page, product.page.parent)
        self.assertEqual(category.page.slug, product.page.parent.slug)

    def test_product_return_page_by_sync_tree(self):
        """
        If product page have parent, category sync tree should do nothing
        """
        product = self.create_product(slug='seventh')
        product.page.parent = self.root_category.page
        product.page.save()
        product.save()  # category.save() hooks tree sync
        self.assertEqual(product.page.parent, self.root_category.page)


class TestProduct(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_id = 1
        cls.category = catalog_models.MockCategory.objects.create(name='some category', id=cls.category_id)

        cls.test_popular_product = catalog_models.MockProduct.objects.create(
            name="Popular",
            price=20,
            category=cls.category,
            in_stock=10,
            is_popular=True,
        )
        catalog_models.MockProduct.objects.create(
            name="unpopular #1",
            price=20,
            category=cls.category,
            in_stock=10,
            is_popular=False,
        )
        catalog_models.MockProduct.objects.create(
            name="unpopular #2",
            price=20,
            category=catalog_models.MockCategory.objects.create(name='another category', id=777),
            in_stock=10,
            is_popular=False,
        )

    def test_popular_products(self):
        """Should be one popular product."""
        popular = catalog_models.MockProduct.objects.filter(is_popular=True)

        self.assertEqual(len(popular), 1)
        self.assertEqual(popular[0].name, self.test_popular_product.name)

    def test_get_product_by_category(self):
        """We can get products related to category by category_id or Category instance"""
        products_by_instance = (
            catalog_models.MockProduct.objects.filter_descendants(self.category)
        )

        self.assertEqual(products_by_instance.count(), 2)

        for products_by_instance in products_by_instance:
            self.assertEqual(products_by_instance.category, self.category)


class Tag(TestCase):

    # @todo #162:60m Create fixtures for tags.
    #  Copy from SE all tags fixtures creation logic.
    #  Then move `shopelectro.tests.tests_models.TagModel` to this class.

    @unittest.skip
    def test_double_named_tag_saving(self):
        """Two tags with the same name should have unique slugs."""
        def save_doubled_tag(tag_from_):
            group_to = catalog_models.MockTagGroup.objects.exclude(id=tag_from_.group.id).first()
            tag_to_ = catalog_models.MockTag(
                group=group_to, name=tag_from_.name, position=tag_from_.position
            )
            # required to create `tag.products` field
            tag_to_.save()
            tag_to_.products.set(tag_from.products.all())
            tag_to_.save()
            return tag_to_
        tag_from = catalog_models.MockTag.objects.first()
        tag_to = save_doubled_tag(tag_from)
        self.assertNotEqual(tag_from.slug, tag_to.slug)

    def test_tag_doubled_save_slug_postfix(self):
        """Tag should preserve it's slug value after several saves."""
        group = catalog_models.MockTagGroup.objects.create(name='Напряжение вход')
        tag = catalog_models.MockTag.objects.create(
            name='12 В',
            group=group
        )
        self.assertEqual(tag.slug, '12-v')
        tag.save()
        self.assertEqual(tag.slug, '12-v')

    def test_long_name(self):
        """
        Tag should accept long names.

        Slug length has limited limited size `catalog.models.MAX_SLUG_LENGTH`.
        It may create problems for tag with long name.
        """
        name = 'Имя ' * 50
        group = catalog_models.MockTagGroup.objects.first()
        try:
            tag = catalog_models.MockTag.objects.create(group=group, name=name)
            self.assertLessEqual(len(tag.slug), catalog.models.SLUG_MAX_LENGTH)
        except DataError as e:
            self.assertTrue(False, f'Tag has too long name. {e}')

    def test_order_by_alphanumeric(self):
        ordered_tags = [
            catalog_models.MockTag(name=name)
            for name in [
                'a', 'b', '1 A', '2.1 A', '1.2 В', '1.2 В', '1.6 В', '5 В', '12 В',
            ]
        ]

        # shuffle just in case
        catalog_models.MockTag.objects.bulk_create(shuffle(ordered_tags))

        for i, tag in enumerate(catalog_models.MockTag.objects.order_by_alphanumeric()):
            self.assertEqual(tag, ordered_tags[i])

    def test_slugify_conflicts(self):
        slugs = [
            catalog_models.MockTag.objects.create(name=name).slug
            for name in ['11 A', '1/1 A', '1 1 A']
        ]

        self.assertEqual(len(slugs), len(set(slugs)), msg=slugs)
