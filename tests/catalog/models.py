from django.db import models
from django.core.urlresolvers import reverse

from catalog.models import AbstractCategory, AbstractProduct

from pages.models import SyncPageMixin, CustomPage


class MockCategory(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug,))


class MockCategoryWithDefaultPage(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'

    @classmethod
    def get_default_parent(cls):
        """You can override this method, if need a default parent"""
        return CustomPage.objects.get(slug='catalog')

    def get_absolute_url(self):
        return reverse('catalog:category', args=(self.page.slug, ))


class MockProduct(AbstractProduct, SyncPageMixin):
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
