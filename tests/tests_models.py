"""
Defines tests for models in Catalog app
"""
import os.path

from django.core.files.images import ImageFile
from django.apps.registry import apps
from django.conf import settings
from django.db import models
from django.test import TestCase

from pages.models import ModelPage, CustomPage, FlatPage
from images.models import Image
import tests


class AbstractModelsTests(TestCase):

    @staticmethod
    def create_page(model: models.Model, **extra_field) -> models.Model:
        return model.objects.create(**{'h1': 'Test h1', **extra_field})

    @staticmethod
    def create_related_entity(number=0):
        name = 'entity_#{}'.format(number)
        model = apps.get_model(settings.ENTITY_MODEL)
        product = model.objects.create(name=name)
        return product

    @staticmethod
    def get_page(model: models.Model, name: str) -> [models.Model] or []:
        return model.objects.filter(h1=name)


class CustomPageTests(AbstractModelsTests):
    def test_get_absolute_url(self):
        page = self.create_page(CustomPage, slug='')

        self.assertIn(page.slug, page.url)


class FlatPageTest(AbstractModelsTests):
    @classmethod
    def setUpClass(cls):
        super(FlatPageTest, cls).setUpClass()

        def create_flat_page(parent=None):
            return cls.create_page(
                FlatPage, slug='page_of_{}'.format(getattr(parent, 'slug', 'ROOT')), parent=parent)

        page = create_flat_page()
        child_page = create_flat_page(parent=page)
        deep_child_page = create_flat_page(parent=child_page)
        cls.pages = [page, child_page, deep_child_page]

    def test_is_section(self):
        root_page, *_ = self.pages
        self.assertTrue(root_page.is_section)

    def test_get_absolute_url(self):
        urls = [page.url for page in self.pages]
        slugs = [page.slug for page in self.pages]

        for url, slug in zip(urls, slugs):
            self.assertIn(slug, url)


class ModelPageTest(AbstractModelsTests):

    def setUp(self):
        self.product = self.create_related_entity()
        self.page = self.product.page

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), self.page.url)


class PageMixinTest(AbstractModelsTests):

    def setUp(self):
        self.entity = self.create_related_entity()
        self.name = self.entity.name

    def test_save_page_after_save_entity(self):
        page = self.get_page(ModelPage, self.name)

        self.assertTrue(page)

    def test_delete_page_after_delete_entity(self):
        self.entity.delete()
        page = self.get_page(ModelPage, self.name)

        self.assertFalse(page)

    def test_update_page_after_update_entity(self):
        def update_parent(parent=None):
            self.entity.parent = parent
            self.entity.save()

        entity_parent = self.create_related_entity(number=1)
        update_parent(entity_parent)

        self.assertEqual(entity_parent.page, self.entity.page.parent)

        update_parent()
        self.assertEqual(self.entity.parent, None)
        self.assertNotEqual(entity_parent.page, self.entity.page.parent)



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


class ImageTests(AbstractModelsTests):
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
        self.page = self.create_page(CustomPage, slug='')
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
