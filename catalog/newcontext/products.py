from functools import lru_cache

from django import http
from django.conf import settings
from django.db.models import QuerySet

from catalog.newcontext.context import Context, Products, Tags
from catalog.models import AbstractCategory
from refarm_pagination.context import PaginationContext


class SortingOption:
    def __init__(self, index=0):
        options = settings.CATEGORY_SORTING_OPTIONS[index]
        self.label = options['label']
        self.field = options['field']
        self.direction = options['direction']

    @property
    def directed_field(self):
        return self.direction + self.field


class ActiveProducts(Products):

    def __init__(self, products: Products):
        self._products = products

    def qs(self):
        return self._products.qs().active()


class OrderedProducts(Products):

    def __init__(self, products: Products, sorting_index=0):
        self._products = products
        self._sorting_index = sorting_index

    def qs(self):
        return self._products.qs().order_by(
            SortingOption(index=self._sorting_index).directed_field,
        )


class ProductsByCategory(Products):

    def __init__(self, products: Products, category: AbstractCategory):
        self._products = products
        self._category = category

    def qs(self):
        return self._products.qs().filter_descendants(self._category)


class TaggedProducts(Products):

    def __init__(self, products: Products, tags: Tags):
        self._products = products
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if tags.exists():
            return self._products.qs().tagged(tags)
        else:
            return self._products.qs()


class ProductBrands(Context):

    def __init__(self, products: Products, tags: Tags):
        self._products = products
        self._tags = tags

    def context(self):
        products = list(self._products.qs())
        brands = self._tags.qs().get_brands(products)

        product_brands = {
            product.id: brands.get(product)
            for product in products
        }

        return {
            'product_brands': product_brands,
        }


class ProductImages(Context):

    def __init__(self, products: Products, images: QuerySet):
        self._products = products
        self._images = images

    def context(self):
        page_product_map = {
            product.page: product
            for product in self._products.qs()
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

    def __init__(self, products: Products, url: str, page_number: int, per_page: int):
        if (
            page_number < 1 or
            per_page not in settings.CATEGORY_STEP_MULTIPLIERS
        ):
            raise http.Http404('Page does not exist.')

        self._products = products
        self._page_number = page_number
        self._pagination = PaginationContext(url, page_number, per_page, self._products.qs())

    @lru_cache()
    def _pagination_context(self):
        return self._pagination.context()

    def qs(self):
        return self._pagination_context()['page'].object_list

    def context(self):
        return {
            **super().context(),
            'paginated': self._pagination_context(),
        }
