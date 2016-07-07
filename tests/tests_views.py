"""
Defines tests for views in Catalog app
"""

from django.test import TestCase
from pages.models import Post, get_crumbs
from django.core.urlresolvers import reverse
from .model_factory import set_default_posts
from django.conf import settings


class PostTests(TestCase):

    urls = 'tests.urls'

    def setUp(self):
        set_default_posts(self)

    def tearDown(self):
        Post.objects.all().delete()

    def test_posts_types_list(self):
        """
        Blog pages list should contain all post types
        """
        url = reverse('pages:post_types')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            settings.APP_BLOG_POST_TYPES['navigation']['name'])
        self.assertContains(response,
                            settings.APP_BLOG_POST_TYPES['news']['name'])

    def test_empty_posts_list(self):
        """
        Empty pages list should return 200 response
         and user friendly message
        """
        self.tearDown()
        url = reverse('pages:posts', args=('news',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no posts yet')
        self.setUp()  # restore mock objects after over removing

    def test_not_found_posts_list(self):
        """Not existing posts list should return 404 status code"""
        url = '/pages/se-ipo/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_posts_list(self):
        """
        List of existing pages should return 200 response
        And list names, of course
        """

        url = reverse('pages:posts', args=('article',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Why Fenich called as new Steve Jobs")

    def test_post_not_found(self):
        """Not found page should return 404 code."""

        url = reverse(
            'pages:navigation',
            kwargs={'slug_': 987654}  # not existing id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_by_id(self):
        """Existing page should return 200 response"""

        url = reverse(
            'pages:news',
            kwargs={'slug_': self.test_news_post.slug}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class BreadcrumbsTests(TestCase):

    urls = 'tests.urls'

    def setUp(self):
        set_default_posts(self)

    def tearDown(self):
        Post.objects.all().delete()

    def test_get_crumbs_names_by_post(self):
        """
        by given post _get_crumbs should return valid crumb names
        """
        crumbs = get_crumbs(self.test_news_post)
        self.assertEqual(crumbs[0].name, settings.CRUMBS['main'])
        self.assertEqual(crumbs[1].name, self.test_news_post.get_type_name())
        self.assertEqual(crumbs[2].name, self.test_news_post.name)

    def test_get_crumbs_aliases_by_post(self):
        """
        by given post _get_crumbs should return crumbs with:
            1. empty alias for last crumb
            2. filled aliases for every other crumb
        """
        crumbs = get_crumbs(self.test_news_post)
        self.assertEqual(crumbs[0].alias, '/')
        self.assertEqual(crumbs[1].alias,
                         reverse('pages:posts', args=('news',)))
        self.assertEqual(crumbs[2].alias, '')

    def test_get_crumbs_names_by_page(self):
        """
        by given page _get_crumbs should return valid crumb names
        """
        crumbs = get_crumbs(settings.CRUMBS['pages'])
        self.assertEqual(crumbs[0].name, settings.CRUMBS['main'])
        self.assertEqual(crumbs[1].name, settings.CRUMBS['pages'])

    def test_get_crumbs_aliases_by_page(self):
        """
        by given page _get_crumbs should return valid crumbs
        """
        crumbs = get_crumbs(settings.CRUMBS['pages'])
        self.assertEqual(crumbs[0].alias, '/')
        self.assertEqual(crumbs[1].alias, '')

    def test_posts_list_breadcrumbs(self):
        """
        Post list should have default breadcrumbs
        """
        url = reverse('pages:post_types')
        response = self.client.get(url)
        self.assertContains(response, settings.CRUMBS['main'])
        self.assertContains(response, settings.CRUMBS['pages'])

    def test_post_breadcrumbs(self):
        """
        Post page should have default breadcrumbs
        """
        url = reverse(
            'pages:news',
            kwargs={'slug_': self.test_news_post.slug}
        )
        response = self.client.get(url)
        self.assertContains(response, settings.CRUMBS['main'])
        self.assertContains(
            response,
            self.test_news_post.get_type_name()
        )
        self.assertContains(response, self.test_news_post.name)
