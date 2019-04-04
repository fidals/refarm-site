from django.db import models

from catalog.models import AbstractPosition, AbstractProduct, AbstractCategory
from pages.models import SyncPageMixin


class MockEcommerceCategory(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'


class MockEcommerceProduct(AbstractPosition, AbstractProduct, SyncPageMixin):
    category = models.ForeignKey(
        MockEcommerceCategory, on_delete=models.CASCADE,
        null=True, related_name='products',
        db_index=True
    )
