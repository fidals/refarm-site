from functools import partial

from django.apps.registry import apps
from django.conf import settings
from django.db import models
from django.test import TestCase

from pages.models import ModelPage, CustomPage, FlatPage, Page


def create_page(model: models.Model, **extra_field) -> models.Model:
    return model.objects.create(**{'name': 'Test h1', **extra_field})


def create_entity(model_path, **kwargs):
    model = apps.get_model(model_path)
    return model.objects.create(**kwargs)

create_test_entity_with_sync = partial(create_entity, model_path=settings.ENTITY_MODEL_WITH_SYNC)


class PageTests(TestCase):
    def setUp(self):
        self.custom_page = create_page(CustomPage, slug='')
        self.model_page = create_page(ModelPage, name='Unique h1')
        self.flat_page = create_page(FlatPage, name='Another unique h1')
        self.child_flat_page = create_page(FlatPage, name='Child unique h1', parent=self.flat_page)

    def get_ancestors(self):
        ancestors = self.child_flat_page.get_ancestors()
        ancestors_without_self = self.child_flat_page.get_ancestors(include_self=False)
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
        page = create_page(Page)

        self.assertTrue(page.slug)


class CustomPageTests(TestCase):
    def test_should_get_only_custom_type_pages(self):
        types = [CustomPage, FlatPage, ModelPage]

        for type in types:
            create_page(type)

        custom_pages = CustomPage.objects.all()
        truthy, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truthy)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_custom_type_pages(self):
        page = create_page(CustomPage)

        self.assertEqual(page.type, Page.CUSTOM_TYPE)

    def test_get_absolute_url(self):
        page = create_page(CustomPage, slug='')

        self.assertIn(page.slug, page.url)


class FlatPageTests(TestCase):
    def setUp(self):

        def create_flat_page(parent=None):
            return create_page(
                FlatPage, slug='page_of_{}'.format(getattr(parent, 'slug', 'ROOT')), parent=parent)

        page = create_flat_page()
        child_page = create_flat_page(parent=page)
        self.pages = [page, child_page]

    def test_should_get_only_custom_type_pages(self):
        types = [FlatPage, CustomPage, ModelPage]

        for type in types:
            create_page(type)

        custom_pages = FlatPage.objects.all()
        truthy, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truthy)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_flat_pages(self):
        page = create_page(FlatPage)

        self.assertEqual(page.type, Page.FLAT_TYPE)

    def test_url(self):
        urls = [page.url for page in self.pages]
        slugs = [page.slug for page in self.pages]

        for url, slug in zip(urls, slugs):
            self.assertIn(slug, url)


class ModelPageTests(TestCase):

    def setUp(self):
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.product = create_test_entity_with_sync(name='Test entity')
        self.page = self.product.page

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), self.page.url)


class SyncPageMixinTests(TestCase):
    @staticmethod
    def get_page(name):
        return ModelPage.objects.filter(name=name).first()

    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = create_test_entity_with_sync(name=self.name)

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

        entity_parent = create_test_entity_with_sync(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)


class PageMixin(TestCase):
    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = create_test_entity_with_sync(name=self.name)

    def test_update_page_after_update_entity(self):
        def set_parent(parent=None):
            self.entity.parent = parent
            self.entity.save()

        entity_parent = create_test_entity_with_sync(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)

    def test_default_parent(self):
        self.assertEqual(self.entity.page.parent, self.default_parent)
