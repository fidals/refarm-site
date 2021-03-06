import hashlib
import os

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from sorl import thumbnail
from sorl.thumbnail import delete


class ImageField(thumbnail.ImageField):

    def generate_filename(self, instance, filename):
        """Reloaded this method. See `django.db.models.fields.files.FileField`."""
        f = getattr(instance, self.name).file
        _, extension = os.path.splitext(filename)
        file_hash = hashlib.md5(f.read()).hexdigest()
        models_folder_name = type(instance.model).__name__.lower()
        filename = '/'.join([
            models_folder_name,
            str(instance.model.pk),
            file_hash + extension
        ])
        return self.storage.generate_filename(filename)


class ImageQuerySet(models.QuerySet):

    def get_main_images_by_pages(self, pages) -> dict:
        pages = list(pages)

        images_query = (
            self.filter(object_id__in=[page.id for page in pages], is_main=True)
        )

        if not images_query.exists():
            return {}

        return {
            page: image
            for image in images_query for page in pages
            if image.object_id == page.id
        }


class ImageManager(models.Manager.from_queryset(ImageQuerySet)):

    def get_main_images_by_pages(self, pages) -> dict:
        return self.get_queryset().get_main_images_by_pages(pages)


class Image(models.Model):
    """
    Architect thoughts:
    One Django cook book recommend us to use Image class.
    And to use sorl app for image fields.
    Django by Example, chapter 5. http://bit.ly/django-by-example-book
    """
    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')

    objects = ImageManager()

    # <--- Generic relation fields | http://bit.ly/django-generic-relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    model = GenericForeignKey('content_type', 'object_id')
    # --->

    title = models.CharField(max_length=400, blank=True, verbose_name=_('title'))
    slug = models.SlugField(max_length=400, blank=True, db_index=True, verbose_name=_('slug'))
    description = models.TextField(default='', blank=True, verbose_name=_('description'))
    created = models.DateField(auto_now_add=True, verbose_name=_('created'))
    image = ImageField(verbose_name=_('image'))
    is_main = models.BooleanField(default=False, db_index=True, verbose_name=_('is main'))

    def __str__(self):
        return self.title

    def __getattribute__(self, name):
        """Some fields should give default value."""
        attr = super(Image, self).__getattribute__(name)
        if name in ['title'] and not attr:
            return self.slug
        return attr

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
        blank=True,
    )

    @property
    def main_image(self) -> models.ImageField:
        main_image = self.images.filter(is_main=True)
        return main_image.first().image if main_image.exists() else None
