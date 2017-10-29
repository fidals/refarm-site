import os.path

from django.core.files.images import ImageFile
from django.db import models
from django.test import TestCase

from pages.models import CustomPage
from images.models import Image

from tests import images


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


class TestImage(TestCase):
    """
    Assume this:
     - Page - model with few images. type(page.images) == QuerySet<Image>
     - Image - model with one ImageField
       and image metadata: slug, date_created, is_main, etc.
     - ImageField - wrapper around image file
    """

    IMG_PATH = os.path.join(os.path.dirname(images.__file__), 'assets/deer.jpg')
    IMG_SLUG = 'one-two'
    page = None
    image_model = None

    def setUp(self):
        super().setUp()
        self.page = CustomPage.objects.create(h1='Test h1', slug='')
        self.image_model = create_image_model(
            model=self.page,
            filename=self.IMG_PATH,
            slug=self.IMG_SLUG
        )

    def tearDown(self):
        self.page.delete()
        self.image_model.delete()
        super().tearDown()

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
