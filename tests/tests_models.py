"""
Defines tests for models in Catalog app
"""

import os.path

from django.test import TestCase
from django.conf import settings
from django.core.files.images import ImageFile
from django.db.models import Model

from pages.models import Page, get_or_create_struct_page
from images.models import Image


import tests


def create_default_page():
    return Page.objects.create(
        slug='default-page-1',
        title='Default page #1',
    )


class PageTests(TestCase):

    @staticmethod
    def delete_index_page():
        page = Page.objects.filter(slug='index').first()
        if page:
            page.delete()

    def test_default_page_creation(self):
        """Default page should have correct type and empty model relation"""
        page = create_default_page()
        self.assertEqual(page.type, page.FLAT_TYPE)
        self.assertEqual(page.model, None)

    def test_custom_page_creation(self):
        """
        Custom page should have correct type, model relation and
        should have field data configured in settings
        """
        self.delete_index_page()
        page = get_or_create_struct_page(slug='index')
        self.assertEqual(page.type, page.CUSTOM_TYPE)
        self.assertEqual(page.model, None)
        self.assertEqual(page.title, settings.PAGES['index']['title'])

    def test_custom_page_get_or_create(self):
        """
        Get_or_create method for custom pages
        should just get page, if it exists. Method shouldn't choose page data
        """
        test_title = 'My tests cool title'
        page = get_or_create_struct_page(slug='index')
        page.title = test_title
        page.save()
        page = get_or_create_struct_page(slug='index')
        self.assertEqual(page.title, test_title)


def open_file(filename: str):
    try:
        file = open(filename, mode='rb')
    except FileNotFoundError:
        raise FileNotFoundError('Put file with name ' + filename)
    return file


def create_image_model(model: Model, filename: str, slug: str):
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
        self.page = create_default_page()
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
        """Every model should have at least one main image"""
        self.assertIsNotNone(self.page.main_image)
        self.image_model.is_main = False
        self.image_model.save()
        self.assertIsNotNone(self.page.main_image)

    def test_get_main_image(self):
        """Page should have not more than one main image"""
        image_model = self.image_model
        # set image model as main for page
        image_model.is_main = True
        image_model.save()
        self.assertEquals(image_model.image, self.page.main_image)

    def test_update_main_image(self):
        """Page should have not more than one main image"""
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

