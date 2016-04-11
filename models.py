from django.db import models


class Page(models.Model):
    "Page of site"
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    is_text_published = models.BooleanField()

    def __str__(self): return self.name
