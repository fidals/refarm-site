"""
Defines tests for views in Catalog app
"""

from django.test import TestCase, override_settings
from blog.models import Post, get_crumbs
from django.core.urlresolvers import reverse
from . import config_factory
from .model_factory import set_default_posts
from django.conf import settings


@override_settings(APP_BLOG_POST_TYPES=config_factory.get_usual())
class ViewsTests(TestCase):

    urls = 'tests.urls'

    def setUp(self):
        set_default_posts(self)

    def tearDown(self):
        Post.objects.all().delete()

    def test_empty_posts_list(self):
        """
        Empty blog pages list should return 200 response
         and user friendly message
        """
        self.tearDown()
        url = reverse('blog:posts_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There is no pages yet")
        self.setUp()  # restore mock objects after over removing

    def test_posts_list(self):
        """
        List of existing blog pages should return 200 response
        And list names, of course
        """

        url = reverse('blog:posts_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ShopElectro go to IPO")
        self.assertContains(response, "Why Fenich called as new Steve Jobs")

    def test_post_not_found(self):
        """Not found page should return 404 code."""

        url = reverse(
            'blog:navigation',
            kwargs={'post_id': 987654}  # not existing id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_by_id(self):
        """Existing page should return 200 response"""

        url = reverse(
            'blog:news',
            kwargs={'post_id': self.test_news_post.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(crumbs[1].alias, reverse('blog:posts_list'))
        self.assertEqual(crumbs[2].alias, '')

    def test_get_crumbs_names_by_blog_page(self):
        """
        by given blog page _get_crumbs should return valid crumb names
        """
        crumbs = get_crumbs(settings.CRUMBS['blog'])
        self.assertEqual(crumbs[0].name, settings.CRUMBS['main'])
        self.assertEqual(crumbs[1].name, settings.CRUMBS['blog'])

    def test_get_crumbs_aliases_by_blog_page(self):
        """
        by given blog page
        _get_crumbs should return valid crumbs
        """
        crumbs = get_crumbs(settings.CRUMBS['blog'])
        self.assertEqual(crumbs[0].alias, '/')
        self.assertEqual(crumbs[1].alias, '')

    def test_posts_list_breadcrumbs(self):
        """
        Post list should have default breadcrumbs
        """
        url = reverse('blog:posts_list')
        response = self.client.get(url)
        self.assertContains(response, settings.CRUMBS['main'])
        self.assertContains(response, settings.CRUMBS['blog'])

    def test_post_breadcrumbs(self):
        """
        Post page should have default breadcrumbs
        """
        url = reverse(
            'blog:news',
            kwargs={'post_id': self.test_news_post.id}
        )
        response = self.client.get(url)
        self.assertContains(response, settings.CRUMBS['main'])
        self.assertContains(
            response,
            self.test_news_post.get_type_name()
        )
        self.assertContains(response, self.test_news_post.name)
