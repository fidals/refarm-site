import random
import string
from itertools import chain, groupby
from operator import attrgetter
from typing import Dict, Iterable, List, Tuple
from uuid import uuid4

from django.conf import settings
from django.utils.text import slugify
from unidecode import unidecode

import mptt
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


def randomize_slug(slug: str) -> str:
    slug_hash = ''.join(
        random.choices(string.ascii_lowercase, k=settings.SLUG_HASH_SIZE)
    )
    return f'{slug}_{slug_hash}'


class AdminTreeDisplayMixin(object):

    def get_admin_tree_title(self):
        """
        Returns string that used as title of entity in sidebar at admin panel
        """
        return '[{id}] {name}'.format(id=self.id, name=self.name)


class CategoryQuerySet(mptt.querysets.TreeQuerySet):
    def active(self):
        return self.filter(page__is_active=True)


class CategoryManager(
    models.Manager.from_queryset(CategoryQuerySet),
    mptt.managers.TreeManager
):
    def get_root_categories_by_products(self, products: models.QuerySet) -> dict:
        root_categories = self.root_nodes()

        if not root_categories.exists():
            return {}

        return {
            product: root_category
            for product in products for root_category in root_categories
            if root_category.is_ancestor_of(product.category)
        }

    def active(self):
        return self.get_queryset().active()


class AbstractCategory(mptt.models.MPTTModel, AdminTreeDisplayMixin):

    objects = CategoryManager()

    class Meta:
        abstract = True
        unique_together = ('name', 'parent')
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    name = models.CharField(max_length=1000, db_index=True, verbose_name=_('name'))
    parent = mptt.models.TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent'),
    )

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.get_absolute_url()

    def get_children_sorted_by_position(self):
        """Get active category's children and sort them by Position field"""
        return (
            self.get_children()
                .filter(page__is_active=True)
                .order_by('page__position', 'name')
                .select_related('page')
        )


class ProductQuerySet(models.QuerySet):

    def get_offset(self, start, step):
        return self[start:start + step]

    def get_by_category(self, category: models.Model) -> models.QuerySet:
        return self.filter(category__in=category.get_descendants(True))

    def get_category_descendants(self, category: models.Model):
        """Return products with prefetch pages and images."""
        return (
            self.prefetch_related('page__images')
            .select_related('page')
            .get_by_category(category)
        )

    def filter_by_categories(self, categories: Iterable[AbstractCategory]):
        """Filter products by given categories."""
        return (
            self.select_related('page')
            .select_related('category')
            .prefetch_related('page__images')
            .filter(category__in=categories, price__gt=0)
        )

    def active(self):
        return self.filter(page__is_active=True)

    def tagged(self, tags):
        # Distinct because a relation of tags and products is M2M.
        # We do not specify the args for `distinct` to avoid dependencies
        # between `order_by` and `distinct` methods.

        # Postgres has `SELECT DISTINCT ON`, that depends on `ORDER BY`.
        # See docs for details:
        # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-DISTINCT
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        return self.filter(tags__in=tags).distinct()


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    """Get all products of given category by Category's id or instance."""

    def get_by_category(self, category: models.Model) -> models.QuerySet:
        return self.get_queryset().get_by_category(category)

    def get_category_descendants(self, category: models.Model) -> models.QuerySet:
        """Return products with prefetch pages and images."""
        return self.get_queryset().get_category_descendants(category)

    def active(self):
        return self.get_queryset().active()

    def tagged(self, tags):
        return self.get_queryset().tagged(tags)


class AbstractProduct(models.Model, AdminTreeDisplayMixin):
    """
    Product model.
    Defines basic functionality and primitives for Product in typical e-shop.
    Has n:1 relation with Category.
    """
    objects = ProductManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=255, db_index=True, verbose_name=_('name'))
    price = models.FloatField(
        blank=True,
        default=0,
        db_index=True,
        verbose_name=_('price'),
    )
    in_stock = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_('in stock'),
    )
    is_popular = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('is popular'),
    )

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def parent(self):
        return self.category or None

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product', args=(self.id,))

    def get_root_category(self):
        return self.category.get_root()

    def get_siblings(self, offset):
        return (
            self.__class__.objects
            .active()
            .filter(category=self.category)
            .exclude(id=self.id)
            .prefetch_related('category')
            .select_related('page')[:offset]
        )


# it's called not as `AbstractTagGroup`, because inner `Meta.abstract = True`
# is not arch design, but about ORM hack.
class TagGroup(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid4, editable=False)  # Ignore CPDBear
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):

    def filter_by_products(self, products: Iterable[AbstractProduct]):
        ordering = settings.TAGS_ORDER
        distinct = [order.lstrip('-') for order in ordering]

        return (
            self
            .filter(products__in=products)
            .order_by(*ordering)
            .distinct(*distinct, 'id')
        )

    def get_group_tags_pairs(self) -> List[Tuple[TagGroup, List['Tag']]]:
        grouped_tags = groupby(self.prefetch_related('group'), key=attrgetter('group'))
        return [
            (group, list(tags_))
            for group, tags_ in grouped_tags
        ]

    def get_brands(self, products: Iterable[AbstractProduct]) -> Dict[AbstractProduct, 'Tag']:
        brand_tags = (
            self.filter(group__name=settings.BRAND_TAG_GROUP_NAME)
            .filter_by_products(products)
            .prefetch_related('products')
            .select_related('group')
        )

        return {
            product: brand
            for brand in brand_tags for product in products
            if product in brand.products.all()
        }

    def as_string(  # Ignore PyDocStyleBear
        self,
        field_name: str,
        type_delimiter: str,
        group_delimiter: str,
    ) -> str:
        """
        :param field_name: Only field's value is used to represent tag as string.
        :param type_delimiter:
        :param group_delimiter:
        :return:
        """
        if not self:
            return ''

        group_tags_map = self.get_group_tags_pairs()

        _, tags_by_group = zip(*group_tags_map)

        return group_delimiter.join(
            type_delimiter.join(getattr(tag, field_name) for tag in tags_list)
            for tags_list in tags_by_group
        )

    def as_title(self) -> str:
        return self.as_string(
            field_name='name',
            type_delimiter=settings.TAGS_TITLE_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_TITLE_DELIMITER
        )

    def as_url(self) -> str:
        return self.as_string(
            field_name='slug',
            type_delimiter=settings.TAGS_URL_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_URL_DELIMITER
        )

    def serialize_tags(
        self,
        field_name: str,
        type_delimiter: str,
        group_delimiter: str,
    ) -> str:
        if not self:
            return ''

        group_tags_map = self.get_group_tags_pairs()

        _, tags_by_group = zip(*group_tags_map)

        return group_delimiter.join(
            type_delimiter.join(getattr(tag, field_name) for tag in tags_list)
            for tags_list in tags_by_group
        )

    def serialize_tags_to_url(self) -> str:
        return self.serialize_tags(
            field_name='slug',
            type_delimiter=settings.TAGS_URL_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_URL_DELIMITER
        )

    def serialize_tags_to_title(self) -> str:
        return self.serialize_tags(
            field_name='name',
            type_delimiter=settings.TAGS_TITLE_DELIMITER,
            group_delimiter=settings.TAG_GROUPS_TITLE_DELIMITER
        )

    def parsed(self, raw: str):
        return self.filter(slug__in=Tag.parse_url_tags(raw))


class TagManager(models.Manager.from_queryset(TagQuerySet)):

    def get_queryset(self):
        return (
            super().get_queryset()
            .order_by(*settings.TAGS_ORDER)
        )

    def get_group_tags_pairs(self):
        return self.get_queryset().get_group_tags_pairs()

    def filter_by_products(self, products):
        return self.get_queryset().filter_by_products(products)

    def get_brands(self, products):
        """Get a batch of products' brands."""
        return self.get_queryset().get_brands(products)

    def parsed(self, raw):
        return self.get_queryset().parsed(raw)


class Tag(models.Model):

    class Meta:
        abstract = True
        unique_together = ('name', 'group')

    objects = TagManager()

    uuid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    slug = models.SlugField(default='', unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # same slugify code used in PageMixin object
            self.slug = slugify(
                unidecode(self.name.replace('.', '-').replace('+', '-'))
            )
        tag_is_doubled = (
            self.__class__.objects
            .filter(slug=self.slug)
            .exclude(group=self.group)
            .exists()
        )
        if tag_is_doubled:
            self.slug = randomize_slug(self.slug)
        super(Tag, self).save(*args, **kwargs)

    # @todo #168:15m Move `Tags.parse_url_tags` Tags context.
    #  Depends on se#567
    @staticmethod
    def parse_url_tags(tags: str) -> list:
        groups = tags.split(settings.TAGS_URL_DELIMITER)
        return set(chain.from_iterable(
            group.split(settings.TAG_GROUPS_URL_DELIMITER) for group in groups
        ))
