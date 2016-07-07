from collections import namedtuple
from unidecode import unidecode

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


# Data structure for breadcrumb item
Crumb = namedtuple('Crumb', 'name alias')


class SitePageMixin(models.Model):
    """
    Contains fields which are common for every pages's page.
    Can be easily used across different models.
    Has no database table, since it's defined as abstract in its meta inner class.
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    _title = models.CharField(name='title', max_length=100, null=True, blank=True)
    _h1 = models.CharField(name='h1', max_length=100, null=True, blank=True)
    _menu_title = models.CharField(max_length=30, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    content = models.TextField(null=True, blank=True)
    _date_published = models.DateField(auto_now_add=True, null=True, blank=True)

    @property
    def title(self):
        return self._title or self.name

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def h1(self):
        return self._h1 or self.name

    @h1.setter
    def h1(self, value):
        self._h1 = value

    @property
    def date_published(self):
        if self._date_published:
            return self._date_published
        if hasattr(settings, 'SITE_CREATED'):
            return settings.SITE_CREATED
        return None

    @date_published.setter
    def date_published(self, value):
        self._date_published = value

    @property
    def menu_title(self):
        return self._menu_title or self.name

    @menu_title.setter
    def menu_title(self, value):
        self._h1 = value

    class Meta:
        abstract = True


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
                  reverse('pages:posts', args=(last_item.type,))),
            Crumb(last_item.name, ''),
        )
    elif last_item == settings.CRUMBS['pages']:
        return (
            Crumb(settings.CRUMBS['main'], '/'),
            Crumb(settings.CRUMBS['pages'], ''),
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
        return reverse('pages:' + self.type, args=(self.slug,))

    class Meta:
        ordering = ['position', 'name']
