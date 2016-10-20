"""
Defines tests for models in Catalog app
"""
import os.path
from functools import partial

from django.core.files.images import ImageFile
from django.apps.registry import apps
from django.conf import settings
from django.db import models
from django.test import TestCase

import tests
from pages.models import ModelPage, CustomPage, FlatPage, Page
from images.models import Image


def _create_page(model: models.Model, **extra_field) -> models.Model:
    return model.objects.create(**{'h1': 'Test h1', **extra_field})


def _create_entity(model_path, **kwargs):
    model = apps.get_model(model_path)
    return model.objects.create(**kwargs)

_create_test_entity = partial(_create_entity, model_path=settings.ENTITY_MODEL)
_create_test_entity_with_sync = partial(_create_entity, model_path=settings.ENTITY_MODEL_WITH_SYNC)



class PageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PageTests, cls).setUpClass()
        cls.custom_page = _create_page(CustomPage, slug='')
        cls.model_page = _create_page(ModelPage, h1='Unique h1')
        cls.flat_page = _create_page(FlatPage, h1='Another unique h1')
        cls.child_flat_page = _create_page(FlatPage, h1='Child unique h1', parent=cls.flat_page)

    @classmethod
    def get_ancestors(cls):
        ancestors = cls.child_flat_page.get_ancestors()
        ancestors_without_self = cls.child_flat_page.get_ancestors(include_self=False)
        return ancestors, ancestors_without_self

    @classmethod
    def get_ancestors_fields(cls, *args, **kwargs):
        return cls.child_flat_page.get_ancestors_fields(*args, **kwargs)

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

        has_nested_list = all(isinstance(x, list) for x in ancestors_different_fields)
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
        ancestors_fields = self.get_ancestors_fields('h1')
        is_str_fields = all(isinstance(field, str) for field in ancestors_fields)

        self.assertEqual(2, len(ancestors_fields))
        self.assertTrue(is_str_fields)

    def test_slug_should_auto_generate(self):
        page = _create_page(Page)

        self.assertTrue(page.slug)


class CustomPageTests(TestCase):
    def test_should_get_only_custom_type_pages(self):
        types = [CustomPage, FlatPage, ModelPage]

        for type in types:
            _create_page(type)

        custom_pages = CustomPage.objects.all()
        truly, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truly)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_custom_type_pages(self):
        page = _create_page(CustomPage)

        self.assertEqual(page.type, Page.CUSTOM_TYPE)

    def test_get_absolute_url(self):
        page = _create_page(CustomPage, slug='')

        self.assertIn(page.slug, page.url)


class FlatPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(FlatPageTests, cls).setUpClass()

        def create_flat_page(parent=None):
            return _create_page(
                FlatPage, slug='page_of_{}'.format(getattr(parent, 'slug', 'ROOT')), parent=parent)

        page = create_flat_page()
        child_page = create_flat_page(parent=page)
        cls.pages = [page, child_page]

    def test_should_get_only_custom_type_pages(self):
        types = [FlatPage, CustomPage, ModelPage]

        for type in types:
            _create_page(type)

        custom_pages = FlatPage.objects.all()
        truly, falsy_first, falsy_second = [
            all(isinstance(page, type) for page in custom_pages)
            for type in types
        ]

        self.assertTrue(truly)
        self.assertFalse(falsy_first)
        self.assertFalse(falsy_second)

    def test_should_create_only_flat_pages(self):
        page = _create_page(FlatPage)

        self.assertEqual(page.type, Page.FLAT_TYPE)

    def test_get_absolute_url(self):
        urls = [page.url for page in self.pages]
        slugs = [page.slug for page in self.pages]

        for url, slug in zip(urls, slugs):
            self.assertIn(slug, url)


class ModelPageTests(TestCase):

    def setUp(self):
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.product = _create_test_entity_with_sync(name='Test entity')
        self.page = self.product.page

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), self.page.url)


class SyncPageMixinTests(TestCase):
    @staticmethod
    def get_page(h1):
        return ModelPage.objects.filter(h1=h1).first()

    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = _create_test_entity_with_sync(name=self.name)

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

        entity_parent = _create_test_entity_with_sync(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)


class PageMixin(TestCase):
    def setUp(self):
        self.name = 'Test entity'
        self.default_parent = CustomPage.objects.create(slug='catalog')
        self.entity = _create_test_entity_with_sync(name=self.name)

    def test_update_page_after_update_entity(self):
        def set_parent(parent=None):
            self.entity.parent = parent
            self.entity.save()

        entity_parent = _create_test_entity_with_sync(name='Unique name')
        set_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        set_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertEqual(self.entity.page.parent, self.default_parent)

    def test_default_parent(self):
        self.assertEqual(self.entity.page.parent, self.default_parent)

def open_file(filename: str):
    try:
        file = open(filename, mode='rb')
    except FileNotFoundError:
        raise FileNotFoundError('Put file with name ' + filename)
    return file


def create_image_model(model: models.Model, filename: str, slug: str):
    image_file = ImageFile(open_file(filename))
    image_model = Image.objects.create(
        model=model,
        slug=slug,
        image=image_file
    )
    image_file.close()
    return image_model


class ImageTests(TestCase):
    """
    Assume this:
     - Page - model with few images. type(page.images) == QuerySet<Image>
     - Image - model with one ImageField
       and image metadata: slug, date_created, is_main, etc.
     - ImageField - wrapper around image file
    """

    IMG_PATH = os.path.join(os.path.dirname(tests.__file__), 'assets/deer.jpg')
    IMG_SLUG = 'one-two'
    page = None
    image_model = None

    def setUp(self):
        super(ImageTests, self).setUpClass()
        self.page = _create_page(CustomPage, slug='')
        self.image_model = create_image_model(
            model=self.page,
            filename=self.IMG_PATH,
            slug=self.IMG_SLUG
        )

    def tearDown(self):
        super(ImageTests, self).tearDownClass()
        self.page.delete()
        self.image_model.delete()

    def test_model_has_one_main_image(self):
        """If model has any images, it should have at least one main image"""
        self.assertIsNotNone(self.page.main_image)
        self.image_model.is_main = False
        self.image_model.save()
        self.assertIsNotNone(self.page.main_image)

    def test_get_main_image(self):
        """Page should have only one main image"""
        image_model = self.image_model
        # set image model as main for page
        image_model.is_main = True
        image_model.save()
        self.assertEquals(image_model.image, self.page.main_image)

    def test_update_main_image(self):
        """
        Model should have only one main image
        after updating on of the images as main
        """
        image_model = self.image_model
        # set image model as main for page
        image_model.is_main = True
        image_model.save()

        # create another image model
        another_image_model = create_image_model(self.page, self.IMG_PATH, 'one-another')
        # set new image model as main for page
        another_image_model.is_main = True
        another_image_model.save()

        # only one new image should be main for page
        image_model = Image.objects.get(slug=self.IMG_SLUG)
        self.assertFalse(image_model.is_main)
        self.assertTrue(another_image_model.is_main)
        self.assertEquals(another_image_model.image, self.page.main_image)
        another_image_model.delete()
