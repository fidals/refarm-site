"""
Defines tests for views in Catalog app
"""
from django.test import TestCase
from django.core.urlresolvers import reverse

from pages.models import CustomPage

from tests.catalog.models import MockCategory, MockProduct


class TestView(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Provides initial setup for tests.
        Instantiates two test objects: test_category and test_product.
        :return:
        """
        super(TestView, cls).setUpClass()
        cls.page_index = CustomPage.objects.get_or_create(name='Index', slug='')[0]
        cls.category_tree_page = CustomPage.objects.get_or_create(slug='catalog')[0]

        cls.test_category = MockCategory.objects.create(
            name='Test',
        )
        cls.test_category.page.slug = 'akkumuliatory-aaa'
        cls.test_category.page.position = 1
        cls.test_category.page.save()
        cls.test_product = MockProduct.objects.create(
            name='Test product',
            price=14.88,
            category_id=cls.test_category.id,
            in_stock=25
        )
        cls.test_root = MockCategory.objects.create(
            name='Root',
        )
        cls.test_root.page.slug = 'root'
        cls.test_root.page.save()
        cls.test_medium = MockCategory.objects.create(
            name='Medium',
            parent=cls.test_root,
        )
        cls.test_medium.slug = 'medium'
        cls.test_medium.save()
        cls.test_last = MockCategory.objects.create(
            name='Last',
            parent=cls.test_medium,
        )
        cls.test_last.page.slug = 'last'
        cls.test_last.save()
        cls.test_product_nested = MockProduct.objects.create(
            name='Nested product',
            category_id=cls.test_last.id,
            price=123.45,
            in_stock=2,
        )

    def test_list(self):
        """
        Test category tree view.
        :return:
        """

        url = self.category_tree_page.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')

    def test_category_page(self):
        """
        Tests category page.
        :return:
        """

        response = self.client.get(self.test_category.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')

    def test_product_page(self):
        """
        Test product page.
        :return:
        """
        response = self.client.get(self.test_product.url)
        self.assertEqual(response.status_code, 200)

    def test_category_crumbs(self):
        """Category should have valid crumbs"""
        page = self.test_last.page
        crumbs_to_test = [
            self.page_index.menu_title, self.page_index.get_absolute_url(),

            self.category_tree_page.menu_title,
            self.category_tree_page.get_absolute_url(),

            self.test_root.page.menu_title, self.test_root.get_absolute_url(),

            self.test_medium.page.menu_title,
            self.test_medium.get_absolute_url(),
            page.menu_title,
        ]
        response = self.client.get(page.get_absolute_url())
        for crumb in crumbs_to_test:
            self.assertContains(response, crumb)

    def test_category_tree_crumbs(self):
        """Category tree page should have valid crumbs"""
        page = self.category_tree_page
        crumbs_to_test = [
            self.page_index.menu_title, self.page_index.get_absolute_url(),
            page.menu_title,
        ]
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        for crumb in crumbs_to_test:
            self.assertContains(response, crumb)

    def test_product_crumbs(self):
        """MockProduct should have valid crumbs"""
        page = self.test_product_nested.page
        crumbs_to_test = [
            self.page_index.menu_title, self.page_index.get_absolute_url(),

            self.category_tree_page.menu_title,
            self.category_tree_page.get_absolute_url(),

            self.test_root.page.menu_title, self.test_root.get_absolute_url(),

            self.test_medium.page.menu_title,
            self.test_medium.get_absolute_url(),

            self.test_last.page.menu_title,
            self.test_last.get_absolute_url(),

            page.menu_title,
        ]
        response = self.client.get(page.get_absolute_url())
        for crumb in crumbs_to_test:
            self.assertContains(response, crumb)

    def test_category_tree_page_url(self):
        page = self.category_tree_page
        response = self.client.get(page.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.h1)

    def test_category_page_url(self):
        page = self.test_last.page
        response = self.client.get(page.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_last.name)

    def test_product_page_url(self):
        page = self.test_product.page
        response = self.client.get(page.url)

        self.assertContains(response, self.test_product.name)

    def test_products_without_images(self):
        response = self.client.get(reverse('products_without_images'))
        self.assertEqual(response.status_code, 200)

    def test_products_without_text(self):
        response = self.client.get(reverse('products_without_text'))
        self.assertEqual(response.status_code, 200)
