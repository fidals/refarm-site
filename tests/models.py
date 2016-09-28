from django.db import models

from pages.models import PageMixin


class TestEntity(PageMixin):
    name = models.CharField(max_length=100)
    parent = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return 'so mock wow'
