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

    def test_existing_posts_have_urls(self):
        """Every existing page must have its own url with 200 response"""

        navigation_url = reverse(
            'blog:navigation',
            kwargs={'post_id': self.test_navigation_post.id}
        )
        response = self.client.get(navigation_url)
        self.assertEqual(response.status_code, 200)

        news_url = reverse(
            'blog:news',
            kwargs={'post_id': self.test_news_post.id}
        )
        response = self.client.get(news_url)
        self.assertEqual(response.status_code, 200)

        article_url = reverse(
            'blog:article',
            kwargs={'post_id': self.test_article_post.id}
        )
        response = self.client.get(article_url)
        self.assertEqual(response.status_code, 200)
