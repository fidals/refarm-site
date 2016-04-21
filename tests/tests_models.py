"""
Defines tests for models in Catalog app
"""

from django.test import TestCase
from blog.models import Page
from django.conf import settings


class ModelsTests(TestCase):

    def setUp(self):
        """
        Defines testing data.
        Mock config and tree pages with different types
        """
        settings.APP_BLOG_PAGE_TYPES = {
            'article': {'name': 'Статьи', 'alias': ''},
            'news': {'name': 'Новости', 'alias': 'news'},
            'navigation': {'name': 'Навигация', 'alias': 'navigation'},
        }

        self.test_news_page = Page.objects.get_or_create(
            name='ShopElectro go to IPO only after 15-n investment rounds',
            type='news',
        )[0]

        self.test_navigation_page = Page.objects.get_or_create(
            name='contacts',
            type='navigation'
        )[0]

        self.test_article_page = Page.objects.get_or_create(
            name='Why Fenich called as new Steve Jobs',
        )[0]

    def tearDown(self):
        settings.APP_BLOG_PAGE_TYPES = {}
        Page.objects.all().delete()

    def test_get_page_type(self):
        """News page must be one and only one in our example"""
        news_pages = Page.objects.filter(type='news')
        self.assertEqual(len(news_pages), 1)
        self.assertEqual(news_pages.values_list()[0][0], self.test_news_page.id)

    def test_default_page_type(self):
        """
        First type name in alphabetical order in APP_BLOG_PAGE_TYPES
        must be default type
        """
        article_pages = Page.objects.filter(type='article')
        self.assertEqual(len(article_pages), 1)
        self.assertEqual(
            article_pages.values_list()[0][0],
            self.test_article_page.id
        )
