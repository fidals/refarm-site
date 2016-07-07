"""
Defines tests for models in Catalog app
"""

from django.test import TestCase
from pages.models import Page, get_or_create_struct_page
from django.conf import settings


class ModelsTests(TestCase):

    @staticmethod
    def __create_default_page():
        return Page.objects.create(
            slug='default-page-1',
            title='Default page #1',
        )

    def test_default_page_creation(self):
        """Default page should have correct type and empty model relation"""
        page = self.__create_default_page()
        self.assertEqual(page.type, page.DEFAULT_TYPE)
        self.assertEqual(page.model, None)

    def test_struct_page_creation(self):
        """
        Struct page should have correct type, model relation and
        should have field data configured in settings
        """
        page = get_or_create_struct_page(slug='index')
        self.assertEqual(page.type, page.STRUCT_TYPE)
        self.assertEqual(page.model, None)
        self.assertEqual(page.title, settings.PAGES['index']['title'])

    def test_struct_page_get_or_create(self):
        """
        Get_or_create method for struct pages
        should just get page, if it exists. Method shouldn't choose page data
        """
        test_title = 'My tests cool title'
        page = get_or_create_struct_page(slug='index')
        page.title = test_title
        page.save()
        page = get_or_create_struct_page(slug='index')
        self.assertEqual(page.title, test_title)
