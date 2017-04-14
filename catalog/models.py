from functools import reduce
from typing import Union

from django.db import models
from django.db.models import Q, F, When, Case, Value, BooleanField
from django.core.urlresolvers import reverse
from django.shortcuts import _get_queryset
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models, managers as mptt_managers


def search(term: str, model_type: Union[models.Model, models.Manager, models.QuerySet],
           lookups: list, ordering=None) -> models.QuerySet:
    """Return search results based on a given model"""
    query_set = _get_queryset(model_type)
    query = reduce(lambda q, lookup: q | Q(**{lookup: term}), lookups, Q())

    return (
        query_set.filter(query, page__is_active=True)
            .annotate(
                is_name_start_by_term=Case(When(
                name__istartswith=term, then=Value(True)), default=Value(False),
                output_field=BooleanField())
            )
            .order_by(F('is_name_start_by_term').desc(), *ordering or ('name', ))
    )


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


class ProductManager(models.Manager):
    """Get all products of given category by Category's id or instance."""

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_by_category(self, category: models.Model, ordering: [str]=None) -> models.QuerySet:
        return self.get_queryset().get_by_category(category, ordering)


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
