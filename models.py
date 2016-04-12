from django.db import models
from django.conf import settings


class Page(models.Model):
    "Page of site"
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    is_text_published = models.BooleanField()
    type = models.CharField(max_length=100,
                            choices=settings.APP_BLOG_PAGE_TYPES,
                            default=settings.APP_BLOG_PAGE_TYPES[0])

    def __str__(self): return self.name
