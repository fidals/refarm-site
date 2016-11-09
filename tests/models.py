from django.db import models

from pages.models import CustomPage, PageMixin, SyncPageMixin


class TestEntityWithSync(SyncPageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    def get_absolute_url(self):
        return '/so-mock-wow/'


class TestEntity(PageMixin):
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
