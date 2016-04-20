"""
Defines tests for views in Catalog app
"""

from django.test import TestCase
from blog.models import Page
from django.core.urlresolvers import reverse
from django.conf import settings


class ViewsTests(TestCase):

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

    def test_existing_pages_have_urls(self):
        """Every existing page must have its own url with 200 response"""

        navigation_url = reverse(
            'blog:navigation',
            kwargs={'page_id': self.test_navigation_page.id}
        )
        response = self.client.get(navigation_url)
        self.assertEqual(response.status_code, 200)

        news_url = reverse(
            'blog:news',
            kwargs={'page_id': self.test_news_page.id}
        )
        response = self.client.get(news_url)
        self.assertEqual(response.status_code, 200)

        article_url = reverse(
            'blog:article',
            kwargs={'page_id': self.test_article_page.id}
        )
        response = self.client.get(article_url)
        self.assertEqual(response.status_code, 200)
