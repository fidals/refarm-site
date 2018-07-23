import unittest

from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.db.utils import IntegrityError
from django.test import TestCase


class Redirects(TestCase):

    def test_redirect_from_existing_page(self):
        """`refarm-site.redirects` app should redirect from existing url too."""
        # take some existing `url_from`
        # @todo #360:30m Remove hardcoded fixture data.
        #  Replace `url_from` and `url_to` with urls, generated from db.
        #  It'll be much more short and clear.
        url_from = '/catalog/categories/category-0/tags/6-v/'
        # create redirect from `url_from` to another existing one - `url_to`
        url_to = '/catalog/categories/category-0/'
        Redirect.objects.create(
            site=Site.objects.first(),
            old_path=url_from,
            new_path=url_to
        )

        # `url_from` should redirect to `url_to`
        response = self.client.get(url_from)
        self.assertEqual(response.status_code, 301)

    # @todo #360:60m Add db constraint for looped redirect.
    #  Example of looped redirect:
    #  `/news/one-two/ --> /news/one-two/`
    #  `60m` because schema and data migrations are needed.
    #  And fix test.
    @unittest.expectedFailure
    def test_looped_redirect(self):
        """
        Redirect like `/news/one-two/ --> /news/one-two/` should fail.

        It should meet db constraint while adding.
        """
        # hardcoded fixtures will be fixed with task in test ahead.
        url_from = url_to = '/catalog/categories/category-0/tags/6-v/'
        # should raise exception, but not. Pdd task ahead will fix it.
        with self.assertRaises(IntegrityError):
            Redirect.objects.create(
                site=Site.objects.first(),
                old_path=url_from,
                new_path=url_to
            )
