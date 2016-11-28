import os
import time

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from sorl import thumbnail
from sorl.thumbnail import delete


def model_directory_path(instance, filename):
    def generate_filename(old_name: str, slug: str) -> str:
        _, file_extension = os.path.splitext(old_name)
        return (slug or str(time.time())) + file_extension

    result_filename = generate_filename(filename, instance.slug)
    models_folder_name = type(instance.model).__name__.lower()
    return '{}/{}/{}'.format(
        models_folder_name, instance.model.pk, result_filename)


class Image(models.Model):
    """
    Architect thoughts:
    One Django cook book recommend us to use Image class.
    And to use sorl app for image fields.
    Django by Example, chapter 5. http://bit.ly/django-by-example-book
    """

    # <--- Generic relation fields | http://bit.ly/django-generic-relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveIntegerField()
    model = GenericForeignKey('content_type', 'object_id')
    # --->

    _title = models.CharField(max_length=400, blank=True)
    slug = models.SlugField(max_length=400, blank=True, db_index=True)
    description = models.TextField(default='', blank=True)
    created = models.DateField(auto_now_add=True)
    image = thumbnail.ImageField(upload_to=model_directory_path)

    is_main = models.BooleanField(default=False, db_index=True)

    @property
    def title(self):
        return self._title or self.slug

    @title.setter
    def title(self, value):
        self._title = value

    def __str__(self):
        return self._title

    def save(self, *args, **kwargs):

        siblings = self.model.images.exclude(pk=self.pk)

        if self.is_main:
            # set as main image
            siblings.update(is_main=False)

        # if current image is single for model, it should be main
        if not siblings:
            self.is_main = True

        super(Image, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Image, self).delete(*args, **kwargs)
        delete(self.image)


class ImageMixin(models.Model):
    """
    Inherit your Model from this class to enable images storing in it

    Architect thoughts:
    Only Page model connected with images. Other models, such as Product or Category are not.
    It's because Page model should be connected with images anyway. To handle Flat Page.
    """

    class Meta:
        abstract = True

    # http://bit.ly/django-generic-relations
    images = GenericRelation(
        Image,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='images',
        blank=True
    )

    @property
    def main_image(self) -> models.ImageField:
        main_image = self.images.filter(is_main=True).first()
        return main_image.image if main_image else None
