"""
Defines tests for models in Catalog app
"""

from django.test import TestCase, override_settings
from blog.models import Post, get_default_type
from . import config_factory
from .model_factory import set_default_posts


@override_settings(APP_BLOG_POST_TYPES=config_factory.get_usual())
class ModelsTests(TestCase):

    def setUp(self):
        set_default_posts(self)

    def tearDown(self):
        Post.objects.all().delete()

    def test_get_posts_type(self):
        """News page is single"""
        news_posts = Post.objects.filter(type='news')
        self.assertEqual(len(news_posts), 1)
        self.assertEqual(news_posts.values_list()[0][0], self.test_news_post.id)

    def test_default_posts_type(self):
        """
        First type name in alphabetical order in APP_BLOG_POST_TYPES
         should be default type
        """
        article_posts = Post.objects.filter(type='article')
        self.assertEqual(len(article_posts), 1)
        self.assertEqual(
            article_posts.values_list()[0][0],
            self.test_article_post.id
        )

    def test_get_default_type(self):
        """
        get_default_type() should return type,
         that marked as default in APP_BLOG_POST_TYPES.
        """
        self.assertEqual(get_default_type(), 'news')
