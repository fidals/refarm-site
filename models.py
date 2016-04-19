from django.db import models
from django.conf import settings


def get_types_as_choices():
    """
    Returns pages types as tuple for CharField choices arg
    :return: choices format
    """
    choices = []
    for page_type_id, page_type in settings.APP_BLOG_PAGE_TYPES.items():
        choices.append((page_type_id, page_type['name']))
    return tuple(choices)


class Page(models.Model):
    """Page of site"""
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100,
                            choices=get_types_as_choices(),
                            default=sorted(list(settings.APP_BLOG_PAGE_TYPES))[0])

    def __str__(self): return self.name
