"""
Defines tests for views in Catalog app
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from blog.models import Page
from django.conf import settings


class ViewsTests(TestCase):

    urls = 'tests.urls'

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
            type='navigation',
        )[0]

        self.test_article_page = Page.objects.get_or_create(
            name='Why Fenich called as new Steve Jobs',
        )[0]

    def tearDown(self):
        settings.APP_BLOG_PAGE_TYPES = {}
        Page.objects.all().delete()

    def test_empty_empty_pages_list(self):
        """
        Empty blog pages list must return 200 response
        and user friend message
        """

        Page.objects.all().delete()
        url = reverse('blog:pages_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no pages yet")

        self.setUp()  # restore mock objects after over removing

    def test_pages_list(self):
        """
        List of existing blog pages must return 200 response
        And list names, of course
        """

        url = reverse('blog:pages_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ShopElectro go to IPO")
        self.assertContains(response, "Why Fenich called as new Steve Jobs")

    def test_page_not_found(self):
        """Not found page must return 404 code."""

        url = reverse(
            'blog:navigation',
            kwargs={'page_id': 987654}  # not existing id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_page_by_id(self):
        """Existing page must return 200 response"""

        url = reverse(
            'blog:news',
            kwargs={'page_id': self.test_news_page.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
