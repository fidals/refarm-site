from functools import lru_cache

from django import http
from django.conf import settings

from catalog import typing
from catalog.context import Products, Tags
from images.models import ImageQuerySet
from refarm_pagination.context import PaginationContext


class ProductBrands(Products):

    def __init__(self, products: typing.Products, tags: Tags):
        super().__init__(products)
        self._tags = tags

    def context(self):
        products = list(self._products)
        brands = self._tags.qs().get_brands(products)

        product_brands = {
            product.id: brands.get(product)
            for product in products
        }

        return {
            'product_brands': product_brands,
        }


class ProductImages(Products):

    def __init__(self, products: typing.Products, images: ImageQuerySet):
        super().__init__(products)
        self._images = images

    def context(self):
        page_product_map = {
            product.page: product
            for product in self.products
        }

        images = self._images.get_main_images_by_pages(page_product_map.keys())
        product_images = {
            product.id: images.get(page)
            for page, product in page_product_map.items()
        }

        return {
            'product_images': product_images,
        }


class PaginatedProducts(Products):
    """Slice products and add pagination data to a context."""

    def __init__(
        self, products: typing.Products,
        url: str, page_number: int, per_page: int
    ):
        if (
            page_number < 1 or
            per_page not in settings.CATEGORY_STEP_MULTIPLIERS
        ):
            raise http.Http404('Page does not exist.')
        super().__init__(products)
        self._pagination = PaginationContext(url, page_number, per_page, products)

    @lru_cache()
    def _pagination_context(self):
        return self._pagination.context()

    @property
    def products(self):
        return self._pagination_context()['page'].object_list

    def context(self):
        return {
            **super().context(),
            'paginated': self._pagination_context(),
        }
