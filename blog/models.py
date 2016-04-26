from django.db import models
from django.conf import settings


def get_types_as_choices():
    """
    Returns pages types as a tuple for the CharField's choices arg
    :return: post types in Model choices format
    """
    return tuple(
        (post_type_id, post_type['name'])
        for post_type_id, post_type in settings.APP_BLOG_POST_TYPES.items()
    )


def get_default_type():
    """
    Get default post type from config
    :return: post type id
    """
    for type_id, type_item in settings.APP_BLOG_POST_TYPES.items():
        if 'default' in type_item:
            return type_id
    return settings.APP_BLOG_POST_TYPES.keys()[0]


class Post(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100,
                            choices=get_types_as_choices(),
                            default=get_default_type())

    def __str__(self):
        """:return: name field value"""
        return self.name
