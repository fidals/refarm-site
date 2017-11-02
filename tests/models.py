from django.db import models

from pages.models import CustomPage, PageMixin, SyncPageMixin


class MockEntityWithSync(SyncPageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    def get_absolute_url(self):
        return '/so-mock-wow/'


class MockEntity(PageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(default='/so-mock-wow/')

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    @property
    def url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        return self.slug


class MockEntityWithRelations(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    related_entity = models.ForeignKey(
        'RelatedEntity', on_delete=models.CASCADE, null=True, blank=True)
    another_related_entity = models.ForeignKey(
        'AnotherRelatedEntity', on_delete=models.CASCADE, null=True, blank=True)


class RelatedEntity(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class AnotherRelatedEntity(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
