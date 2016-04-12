from django.db import models


class Page(models.Model):
    "Page of site"
    PAGE_TYPES = (
        ('article', 'Статьи'),
        ('news', 'Новости'),
        ('navi', 'Навигация'),
    )
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    is_text_published = models.BooleanField()
    page_type = models.CharField(max_length=100, choices=PAGE_TYPES, default=PAGE_TYPES[0])

    def __str__(self): return self.name
