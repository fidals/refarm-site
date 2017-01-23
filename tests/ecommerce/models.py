from django.db import models

from catalog.models import AbstractProduct, AbstractCategory
from pages.models import SyncPageMixin


class EcommerceTestCategory(AbstractCategory, SyncPageMixin):
    product_related_name = 'products'


class EcommerceTestProduct(AbstractProduct, SyncPageMixin):
    category = models.ForeignKey(
        EcommerceTestCategory, on_delete=models.CASCADE,
        null=True, related_name='products',
        db_index=True
    )
