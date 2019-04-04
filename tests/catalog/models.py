from django.core.urlresolvers import reverse
from django.db import models

from catalog import models as catalog_models
from pages.models import SyncPageMixin, CustomPage


class MockCategory(catalog_models.AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug,))


class MockCategoryWithDefaultPage(catalog_models.AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug, ))


class MockProduct(
    catalog_models.AbstractPosition,
    catalog_models.AbstractProduct,
    SyncPageMixin
):
    category = models.ForeignKey(
        MockCategory, on_delete=models.CASCADE,
        default=None, related_name='products',
        db_index=True
    )

    def get_absolute_url(self):
        return reverse('product', args=(self.id, ))

    @property
    def image(self):
        return 'no-image-right-now'


class MockTagGroup(catalog_models.TagGroup):
    pass


class MockTag(catalog_models.Tag):
    group = models.ForeignKey(
        MockTagGroup, on_delete=models.CASCADE, null=True, related_name='tags',
    )
