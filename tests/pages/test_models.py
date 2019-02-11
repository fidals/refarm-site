from django.test import TestCase

from pages import db_views
from pages.models import ModelPage, CustomPage, FlatPage, Page, PageTemplate

from tests.models import MockEntity, MockEntityWithSync


def create_instance(with_sync=True, **kwargs):
    cls = with_sync and MockEntityWithSync or MockEntity
    # noinspection PyUnresolvedReferences
    return cls.objects.create(**kwargs)


class TestPage(TestCase):
    def setUp(self):
        super().setUp()
        self.custom_page = CustomPage.objects.create(slug='')
        self.model_page = ModelPage.objects.create(name='Unique h1')
        self.flat_page = FlatPage.objects.create(name='Another unique h1')
        self.child_flat_page = FlatPage.objects.create(
            name='Child unique h1', parent=self.flat_page
        )

    def get_ancestors(self):
        ancestors = self.child_flat_page.get_ancestors(include_self=True)
        ancestors_without_self = self.child_flat_page.get_ancestors()
        return ancestors, ancestors_without_self

    def get_ancestors_fields(self, *args, **kwargs):
        return self.child_flat_page.get_ancestors_fields(*args, **kwargs)

    def test_is_model(self):
        self.assertTrue(self.model_page.is_model)
        self.assertFalse(self.model_page.is_flat)
        self.assertFalse(self.model_page.is_custom)

    def test_is_flat(self):
        self.assertFalse(self.flat_page.is_model)
        self.assertTrue(self.flat_page.is_flat)
        self.assertFalse(self.flat_page.is_custom)

    def test_is_custom(self):
        self.assertFalse(self.custom_page.is_model)
        self.assertFalse(self.custom_page.is_flat)
        self.assertTrue(self.custom_page.is_custom)

    def test_is_root(self):
        self.assertTrue(self.flat_page.is_root)

    def test_get_ancestors_len(self):
        ancestors, ancestors_without_self = self.get_ancestors()

        self.assertEqual(2 , len(ancestors))
        self.assertEqual(1 , len(ancestors_without_self))

    def test_get_ancestors_instance_class(self):
        """Ancestors should be Page's instances"""
        ancestors, ancestors_without_self = self.get_ancestors()

        self.assertTrue(all(map(lambda x: isinstance(x, Page), ancestors)))
        self.assertTrue(all(map(lambda x: isinstance(x, Page), ancestors_without_self)))

    def test_get_ancestors_fields_with_several_args(self):
        """
        If pass several args in get_ancestors_fields,
        return [[field, field, ...], [field, field, ...], ...],
        """
        def is_str_fields(*args):
            return all(isinstance(arg, str)for arg in args)

        ancestors_different_fields = self.get_ancestors_fields('h1', 'slug')

        has_nested_list = all(isinstance(x, tuple) for x in ancestors_different_fields)
        is_nested_list_with_str_fields = all(
            is_str_fields(*fields)
            for fields in zip(*ancestors_different_fields)
        )
        fields_instances = [
            len(instance_fields)
            for instance_fields in ancestors_different_fields
        ]

        self.assertEqual(2, len(ancestors_different_fields))
        self.assertEqual(2, *fields_instances)
        self.assertTrue(has_nested_list)
        self.assertTrue(is_nested_list_with_str_fields)

    def test_get_ancestors_fields_with_one_args(self):
        """
        If pass one arg in get_ancestors_fields, we get [field, field, ...].
        """
        ancestors_fields = self.get_ancestors_fields('name')
        is_str_fields = all(isinstance(field, str) for field in ancestors_fields)

        self.assertEqual(2, len(ancestors_fields))
        self.assertTrue(is_str_fields)

    def test_slug_should_auto_generate(self):
        page = Page.objects.create(name='Test name')

        self.assertTrue(page.slug)

    # @todo #240:30m  Improve DB templates (and views) tests.
    #  Move them to separated module.
    #  Rename theirs `test_display` prefix.
    #  Separate them on small pieces.
    #  Add test for `db_views.Page` with passing context.
    def test_display_seo_fields(self):
        page_with_custom_fields = Page.objects.create(
            name='some page', slug='test', h1='test h1'
        )
        page_view = db_views.Page(page_with_custom_fields, {})
        self.assertEqual(page_view.fields.h1, 'test h1')

        custom_page_template = PageTemplate.objects.create(
            name='test',
            h1='{{ page.name }} - купить в СПб',
        )

        page = Page.objects.create(
            name='different page', template=custom_page_template
        )

        page_view = db_views.Page(page, {'page': page})

        self.assertEqual(page_view.fields.h1, 'different page - купить в СПб')

    def test_display_attribute_uses_template(self):
        template = PageTemplate.objects.create(
            name='test',
            h1='{{ page.h1 }} - template',
        )
        page = Page.objects.create(
            name='different page',
            h1='page h1',
            template=template,
        )
        page_view = db_views.Page(page, {'page': page})
        self.assertEqual(page_view.fields.h1, 'page h1 - template')


class TestCustomPage(TestCase):
    def test_should_get_only_custom_type_pages(self):
        types = [CustomPage, FlatPage, ModelPage]

        for type in types:
            type.objects.create()

        custom_pages = CustomPage.objects.all()
        truthy, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truthy)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_custom_type_pages(self):
        page = CustomPage.objects.create(name='Test name')
        self.assertEqual(page.type, Page.CUSTOM_TYPE)

    def test_get_absolute_url(self):
        page = CustomPage.objects.create(name='Test name', slug='')
        self.assertIn(page.slug, page.url)


class TestFlatPage(TestCase):
    def setUp(self):

        def create_flat_page(parent=None):
            return FlatPage.objects.create(
                slug='page_of_{}'.format(getattr(parent, 'slug', 'ROOT')),
                parent=parent
            )

        page = create_flat_page()
        child_page = create_flat_page(parent=page)
        self.pages = [page, child_page]

    def test_should_get_only_custom_type_pages(self):
        types = [FlatPage, CustomPage, ModelPage]

        for type in types:
            type.objects.create(name='Test name')

        custom_pages = FlatPage.objects.all()
        truthy, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truthy)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_flat_pages(self):
        page = FlatPage.objects.create(name='Test name')
        self.assertEqual(page.type, Page.FLAT_TYPE)

    def test_url(self):
        urls = [page.url for page in self.pages]
        slugs = [page.slug for page in self.pages]
        for url, slug in zip(urls, slugs):
            self.assertIn(slug, url)


class TestModelPage(TestCase):

    def setUp(self):
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.product = create_instance(name='Test entity')
        self.page = self.product.page

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), self.page.url)


class TestSyncPageMixin(TestCase):
    @staticmethod
    def get_page(name):
        return ModelPage.objects.filter(name=name).first()

    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = create_instance(name=self.name)

    def test_default_parent(self):
        self.assertEqual(self.entity.page.parent, self.default_parent)

    def test_save_page_after_save_entity(self):
        page = self.get_page(self.name)
        self.assertTrue(page)

    def test_delete_page_after_delete_entity(self):
        self.entity.delete()
        page = self.get_page(self.name)
        self.assertFalse(page)

    def test_update_page_after_update_entity(self):
        def set_parent(parent=None):
            self.entity.parent = parent
            self.entity.save()

        entity_parent = create_instance(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)


class TestPageMixin(TestCase):
    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = create_instance(name=self.name)

    def test_update_page_after_update_entity(self):
        def set_parent(parent=None):
            self.entity.parent = parent
            self.entity.save()

        entity_parent = create_instance(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)

    def test_sync_page_name(self):
        """Page's name should sync with related entity's name."""
        self.entity.name = 'New name'
        self.entity.save()

        self.assertEqual(self.entity.name, self.entity.page.name)
        
    def test_default_parent(self):
        self.assertEqual(self.entity.page.parent, self.default_parent)
