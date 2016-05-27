from unidecode import unidecode
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from seo.models import SitePageMixin
from seo.models import Crumb


def get_crumbs(last_item):
    """
    Returns specified item ancestors as breadcrumbs
    :param last_item: last crumb's item entity
    :return: crumbs named tuple:
     (('First page', 'one/'), ('Second page', 'two/'),)
    """
    if isinstance(last_item, Post):
        return (
            Crumb(settings.CRUMBS['main'], '/'),
            Crumb(last_item.get_type_name(),
                  reverse('blog:posts', args=(last_item.type,))),
            Crumb(last_item.name, ''),
        )
    elif last_item == settings.CRUMBS['blog']:
        return (
            Crumb(settings.CRUMBS['main'], '/'),
            Crumb(settings.CRUMBS['blog'], ''),
        )
    else:
        raise AttributeError('Wrong last_item argument value')


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


class Post(SitePageMixin, models.Model):
    type = models.CharField(max_length=100,
                            choices=get_types_as_choices(),
                            default=get_default_type())
    slug = models.SlugField()
    position = models.IntegerField(null=False, default=0)

    def get_type_name(self):
        return settings.APP_BLOG_POST_TYPES[self.type]['name']

    def __str__(self):
        """:return: name field value"""
        return self.name

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(unidecode(self.name))
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:' + self.type, args=(self.slug,))

    class Meta:
        ordering = ['position', 'name']
