import random
import string
import typing
from collections import OrderedDict
from itertools import chain
from uuid import uuid4

import mptt
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from catalog.models_expressions import Substring


def randomize_slug(slug: str, hash_size: int) -> str:
    hash_size = hash_size
    slug_hash = ''.join(
        random.choices(string.ascii_lowercase, k=hash_size)
    )
    return f'{slug}_{slug_hash}'


class AdminTreeDisplayMixin(object):

    def get_admin_tree_title(self):
        """
        Returns string that used as title of entity in sidebar at admin panel
        """
        return '[{id}] {name}'.format(id=self.id, name=self.name)


class CategoryQuerySet(mptt.querysets.TreeQuerySet):
    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return (
            self.select_related('page')
            .select_related('parent')
            .prefetch_related('children')
        )

    def active(self):
        return self.filter(page__is_active=True)


class CategoryManager(
    mptt.managers.TreeManager.from_queryset(CategoryQuerySet),
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

    def bind_fields(self):
        """Prefetch or select typical related fields to reduce sql queries count."""
        return (
            self.select_related('page')
            .select_related('category')
            .prefetch_related('page__images')
        )

    def filter_descendants(self, category: models.Model) -> models.QuerySet:
        return self.filter(category__in=category.get_descendants(True))

    def active(self):
        return self.filter(page__is_active=True)

    def tagged(self, tags: 'TagQuerySet'):
        # Distinct because a relation of tags and products is M2M.
        # We do not specify the args for `distinct` to avoid dependencies
        # between `order_by` and `distinct` methods.

        # Postgres has `SELECT DISTINCT ON`, that depends on `ORDER BY`.
        # See docs for details:
        # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-DISTINCT
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        return self.filter(tags__in=tags).distinct()

    def tagged_or_all(self, tags: 'TagQuerySet'):
        return (
            self.tagged(tags)
            if tags.exists()
            else self
        )


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    """Get all products of given category by Category's id or instance."""

    def filter_descendants(self, category: models.Model) -> models.QuerySet:
        return self.get_queryset().filter_descendants(category)

    def active(self):
        return self.get_queryset().active()

    def tagged(self, tags: typing.Iterable['Tag']):
        return self.get_queryset().tagged(tags)


class AbstractPosition(models.Model):
    """
    The smallest unique catalog item.

    In catalog semantics position is a description of physical product variation.
    Only position can have price, vendor code, in stock/cart presence.
    Example:
        1. If a shop sells only one iphone X variation,
        this iphone X will be both Position and Product item.

        2. If some shop sells two iphone X variations: red and black,
        "iphone X" will be Product item,
        "iphone X red" will be both Position and Option item.
    """
    class Meta:
        abstract = True

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


class AbstractOption(AbstractPosition):
    """
    Product variation.

    "iphone X red" can be an option of "iphone X" product.
    Sites may use it as Position or may not use it all in favour of Product.
    """
    class Meta:
        abstract = True


class AbstractProduct(models.Model, AdminTreeDisplayMixin):
    """
    High level catalog item for product.

    On sites side may contain options or may not.
    """
    objects = ProductManager()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=255, db_index=True, verbose_name=_('name'))

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

    SLUG_HASH_SIZE = 5
    SLUG_MAX_LENGTH = 25

    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid4, editable=False)  # Ignore CPDBear
    name = models.CharField(
        max_length=100, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    # @todo #302:30m  Resolve slug code doubling.
    #  See `TagGroup.slug` and `Tag._get_slug`.
    @property
    def slug(self) -> str:
        """Make a slug from the name."""
        # Translate all punctuation chars to "_".
        # It doesn't conflict with `slugify`, which translate spaces to "-"
        # and punctuation chars to "".
        slug = slugify(unidecode(self.name.translate(
            {ord(p): '_' for p in string.punctuation}
        )))

        # Keep the slug length less then SLUG_MAX_LENGTH
        if len(slug) < self.SLUG_MAX_LENGTH:
            return slug

        slug_length = self.SLUG_MAX_LENGTH - self.SLUG_HASH_SIZE - 1
        return randomize_slug(
            slug[:slug_length],
            hash_size=self.SLUG_HASH_SIZE
        )

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):

    def order_by_alphanumeric(self):
        """Sort the Tag by name's alphabetic chars and then by numeric chars."""
        return self.annotate(
            tag_name=Substring(models.F('name'), models.Value('[a-zA-Zа-яА-Я\s\-_,:;]+')),
            tag_value=models.functions.Cast(
                Substring(models.F('name'), models.Value('[0-9]+\.?[0-9]*')),
                models.FloatField(),
        )).order_by('group__position', 'group__name', 'tag_name', 'tag_value')

    def filter_by_products(self, products: typing.Iterable[AbstractProduct]):
        return (
            self
            .filter(products__in=products)
            .distinct()
        )

    def exclude_by_products(self, products: typing.Iterable[AbstractProduct]):
        return (
            self
            .exclude(products__in=products)
            .distinct()
        )

    def group_tags(self) -> typing.Dict[TagGroup, typing.List['Tag']]:
        """
        Return set of group_tag pairs with specific properties.

        Every pair contains tag group and sorted tag list.
        It's sorted alphabetically and then numerically.
        """
        # @todo #STB374:120m Move tag's value to separated field.
        #  Now we have fields like `tag.name == '10 м'`.
        #  But should have smth like this:
        #  `tag.value, tag.group.measure, tag.label == 10, 'м', '10 м'`.
        #  Right now we should do dirty hacks for tags comparing mech.
        ordered = self.prefetch_related('group').order_by_alphanumeric()

        grouped = OrderedDict()
        for tag in ordered:
            if tag.group in grouped:
                grouped[tag.group].append(tag)
            else:
                grouped[tag.group] = [tag]
        return grouped

    def get_brands(self, products: typing.Iterable[AbstractProduct]) -> typing.Dict[AbstractProduct, 'Tag']:
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

        group_tags_map = self.group_tags()
        tags_by_group = list(group_tags_map.values())

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

        group_tags_map = self.group_tags()
        tags_by_group = list(group_tags_map.values())

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

    def order_by_alphanumeric(self):
        return self.get_queryset().order_by_alphanumeric()

    def group_tags(self):
        return self.get_queryset().group_tags()

    def filter_by_products(self, products):
        return self.get_queryset().filter_by_products(products)

    def get_brands(self, products):
        """Get a batch of products' brands."""
        return self.get_queryset().get_brands(products)

    def parsed(self, raw):
        return self.get_queryset().parsed(raw)


class Tag(models.Model):

    SLUG_HASH_SIZE = 5
    SLUG_MAX_LENGTH = 50

    class Meta:
        abstract = True
        unique_together = [('name', 'group'), ('slug', 'group')]

    objects = TagManager()

    uuid = models.UUIDField(default=uuid4, editable=False)
    name = models.CharField(
        max_length=1000, db_index=True, verbose_name=_('name'))
    position = models.PositiveSmallIntegerField(
        default=0, blank=True, db_index=True, verbose_name=_('position'),
    )

    slug = models.SlugField(
        blank=False, unique=False, max_length=SLUG_MAX_LENGTH,
    )

    def __str__(self):
        return self.name

    def _get_slug(self) -> str:
        # Translate all punctuation chars to "_".
        # It doesn't conflict with `slugify`, which translate spaces to "-"
        # and punctuation chars to "".
        slug = slugify(unidecode(self.name.translate(
            {ord(p): '_' for p in string.punctuation}
        )))

        slug = '__'.join([self.group.slug, slug])

        # Keep the slug length less then SLUG_MAX_LENGTH
        if len(slug) < self.SLUG_MAX_LENGTH:
            return slug

        slug_length = self.SLUG_MAX_LENGTH - self.SLUG_HASH_SIZE - 1
        return randomize_slug(
            slug=slug[:slug_length],
            hash_size=self.SLUG_HASH_SIZE
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_slug()
        super(Tag, self).save(*args, **kwargs)

    # @todo #168:15m Move `Tags.parse_url_tags` Tags context.
    #  Depends on se#567
    @staticmethod
    def parse_url_tags(tags: str) -> list:
        groups = tags.split(settings.TAGS_URL_DELIMITER)
        return set(chain.from_iterable(
            group.split(settings.TAG_GROUPS_URL_DELIMITER) for group in groups
        ))
