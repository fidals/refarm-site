from django.test import TestCase

from pages import models


class PageTests(TestCase):
    fixtures = ['catalog.json']

    @property
    def page(self):
        return (
            models.Page.objects
            .active()
            .filter(type=models.Page.MODEL_TYPE)
            .exclude(parent=None)
            .exclude(parent=models.CustomPage.objects.get(slug='catalog'))
            .first()
        )

    def test_breadcrumbs(self):
        ...
