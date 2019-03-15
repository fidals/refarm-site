from django.test import TestCase

from pages import display, models


class Fields(TestCase):
    fixtures = []

    def test_attribute_error(self):
        # noinspection PyTypeChecker
        page = display.Page(None, {})
        with self.assertRaises(AttributeError):
            _ = page.bad_attr


class Page(TestCase):

    def test_plain_field(self):
        page = models.Page.objects.create(
            name='some page', slug='test', h1='test h1'
        )
        self.assertEqual(page.display.h1, 'test h1')

    def test_db_template(self):
        template = models.PageTemplate.objects.create(
            name='test',
            h1='{{ page.name }} - купить в СПб',
        )

        page = models.Page.objects.create(
            name='different page', template=template
        )
        self.assertEqual(page.display.h1, 'different page - купить в СПб')

    def test_context_setter(self):
        template = models.PageTemplate.objects.create(
            name='test',
            h1='{{ some_field }}',
        )

        page = models.Page.objects.create(
            name='different page', template=template
        )
        page.display = {'some_field': 'some_value'}
        self.assertEqual(page.display.h1, 'some_value')

    def test_attribute_uses_template(self):
        template = models.PageTemplate.objects.create(
            name='test',
            h1='{{ page.h1 }} - template',
        )
        page = models.Page.objects.create(
            name='different page',
            h1='page h1',
            template=template,
        )
        self.assertEqual(page.display.h1, 'page h1 - template')

    def test_has_unique_context(self):
        """Two different pages should contain not overlapping display contexts."""
        left_template = models.PageTemplate.objects.create(name='left', h1='{{ tag }}')
        right_template = models.PageTemplate.objects.create(name='right', h1='{{ tag }}')
        left = models.Page.objects.create(name='left', template=left_template)
        right = models.Page.objects.create(name='right', template=right_template)

        left.template.h1, right.template.h1 = '{{ tag }}', '{{ tag }}'
        left.display, right.display = {'tag': 'A'}, {'tag': 'B'}

        self.assertNotEqual(left.display.h1, right.display.h1)

    def test_has_unique_template(self):
        """Two different pages should contain not overlapping display contexts."""
        left_template = models.PageTemplate.objects.create(name='left', h1='{{ tag }}')
        right_template = models.PageTemplate.objects.create(
            name='right', h1='different {{ tag }}'
        )
        left = models.Page.objects.create(name='left', template=left_template)
        right = models.Page.objects.create(name='right', template=right_template)

        left.template.h1 = '{{ tag }}'
        right.template.h1 = 'different {{ tag }}'
        left.display, right.display = {'tag': 'A'}, {'tag': 'A'}

        self.assertNotEqual(left.display.h1, right.display.h1)
