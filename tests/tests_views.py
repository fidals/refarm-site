"""
Defines tests for views in Catalog app
"""

from django.test import TestCase, override_settings
from blog.models import Post
from django.core.urlresolvers import reverse
from . import config_factory
from .model_factory import set_default_posts


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
