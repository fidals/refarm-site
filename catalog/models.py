import random
import string
from itertools import chain, groupby
from operator import attrgetter
from typing import Dict, List, Tuple
from uuid import uuid4

from django.conf import settings
from django.utils.text import slugify
from unidecode import unidecode

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models, managers as mptt_managers


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


class CategoryManager(mptt_managers.TreeManager):
    def get_root_categories_by_products(self, products: models.QuerySet) -> dict:
        root_categories = self.root_nodes()

        if not root_categories.exists():
            return {}

        return {
            product: root_category
            for product in products for root_category in root_categories
            if root_category.is_ancestor_of(product.category)
        }

    def get_active(self):
        return self.get_queryset().filter(page__is_active=True)


class AbstractCategory(mptt_models.MPTTModel, AdminTreeDisplayMixin):

    class Meta:
        abstract = True
        unique_together = ('name', 'parent')
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    objects = CategoryManager()
    name = models.CharField(max_length=255, db_index=True, verbose_name=_('name'))
    parent = mptt_models.TreeForeignKey(
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

    def get_by_category(self, category: models.Model, ordering: [str]=None) -> models.QuerySet:
        ordering = ordering or ['name']
        categories = category.get_descendants(True)

        return self.filter(category__in=categories).order_by(*ordering)

    def get_category_descendants(self, category: models.Model, ordering: [str]=None):
        """Return products with prefetch pages and images."""
        return (
            self.prefetch_related('page__images')
            .select_related('page')
            .get_by_category(category, ordering=ordering)
        )


class ProductManager(models.Manager):
    """Get all products of given category by Category's id or instance."""

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_by_category(self, category: models.Model, ordering: [str]=None) -> models.QuerySet:
        return self.get_queryset().get_by_category(category, ordering)

    def get_category_descendants(self, category: models.Model, ordering: [str]=None) -> models.QuerySet:
        """Return products with prefetch pages and images."""
        return self.get_queryset().get_category_descendants(category, ordering)

    def get_active(self):
        return self.get_queryset().filter(page__is_active=True)


class ProductActiveManager(ProductManager):
    def get_queryset(self):
        return (
            super(ProductActiveManager, self)
            .get_queryset()
            .filter(page__is_active=True)
        )


class AbstractProduct(models.Model, AdminTreeDisplayMixin):
    """
    Product model.
    Defines basic functionality and primitives for Product in typical e-shop.
    Has n:1 relation with Category.
    """
    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    objects = ProductManager()
    actives = ProductActiveManager()
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

    def filter_by_products(self, products: List[AbstractProduct]):
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

    def get_brands(self, products: List[AbstractProduct]) -> Dict[AbstractProduct, 'Tag']:
        brand_tags = (
            self.filter(group__name=settings.BRAND_TAG_GROUP_NAME)
            .prefetch_related('products')
            .select_related('group')
        )

        return {
            product: brand
            for brand in brand_tags for product in products
            if product in brand.products.all()
        }


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

    slug = models.SlugField(default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # same slugify code used in PageMixin object
            self.slug = slugify(
                unidecode(self.name.replace('.', '-').replace('+', '-'))
            )
        doubled_tag_qs = self.__class__.objects.filter(slug=self.slug)
        if doubled_tag_qs:
            self.slug = randomize_slug(self.slug)
        super(Tag, self).save(*args, **kwargs)

    @staticmethod
    def parse_url_tags(tags: str) -> list:
        groups = tags.split(settings.TAGS_URL_DELIMITER)
        return set(chain.from_iterable(
            group.split(settings.TAG_GROUPS_URL_DELIMITER) for group in groups
        ))


def serialize_tags(
    tags: TagQuerySet,
    field_name: str,
    type_delimiter: str,
    group_delimiter: str,
) -> str:
    group_tags_map = tags.get_group_tags_pairs()

    _, tags_by_group = zip(*group_tags_map)

    return group_delimiter.join(
        type_delimiter.join(getattr(tag, field_name) for tag in tags_list)
        for tags_list in tags_by_group
    )


def serialize_tags_to_url(tags: TagQuerySet) -> str:
    return serialize_tags(
        tags=tags,
        field_name='slug',
        type_delimiter=settings.TAGS_URL_DELIMITER,
        group_delimiter=settings.TAG_GROUPS_URL_DELIMITER
    )


def serialize_tags_to_title(tags: TagQuerySet) -> str:
    return serialize_tags(
        tags=tags,
        field_name='name',
        type_delimiter=settings.TAGS_TITLE_DELIMITER,
        group_delimiter=settings.TAG_GROUPS_TITLE_DELIMITER
    )
