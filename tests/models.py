from django.db import models

from pages.models import PageMixin, SyncPageMixin


class TestEntityWithSync(SyncPageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)
    DEFAULT_PARENT_FIELD = {'slug': 'catalog'}

    def get_absolute_url(self):
        return '/so-mock-wow/'


class TestEntity(PageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)
    DEFAULT_PARENT_FIELD = {'slug': 'catalog'}

    def get_absolute_url(self):
        return '/so-mock-wow/'
