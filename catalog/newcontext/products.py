import typing

from django.db.models import QuerySet

from catalog.newcontext.context import Context, Products, Tags
from catalog.models import AbstractCategory


class ActiveProducts(Products):

    def __init__(self, products: Products):
        self._products = products

    def qs(self):
        return self._products.qs().active()


class OrderedProducts(Products):

    def __init__(self, products: Products, req_kwargs):
        self._products = products
        self._sorting_index = self._req_kwargs.get('sorting', 0)

    def qs(self):
        return self._products.qs().order_by(
            SortingOption(index=self._sorting_index).directed_field,
        )

    def context(self):
        return {
            **super().context(),
            'sorting_index': self._sorting_index,
        }


class ProductsByCategory(Products):

    def __init__(self, products: Products, category: AbstractCategory):
        self._products = products
        self._category = category

    def qs(self):
        return self._products.qs().get_category_descendants(self._category)


class ProductsByTags(Products):

    def __init__(self, products: Products, tags_context: Tags):
        self._products = products
        self._tags = tags

    def qs(self):
        tags = self._tags.qs()
        if tags.exists():
            return self._products.qs().tagged(tags)
        else:
            return self._products.qs()


class ProductBrand(Context):

    def __init__(self, products: Products, tags: Tags):
        self._products = products
        self._tags = tags

    def context(self):
        products_qs = self.products.qs()
        brands = self.tags.qs().get_brands(products_qs)

        product_brands = {
            product.id: brands.get(product)
            for product in products_qs
        }

        return {
            'product_brands': product_brands,
        }


class ProductImages

    def __init__(self, products: Products):
        self._products = products

    def context(self):
        page_product_map = {
            product.page: product
            for product in self._products.qs()
        }
        images = Image.objects.get_main_images_by_pages(page_product_map.keys())
        product_images = {
            product: images.get(page)
            for page, product in page_product_map.items()
        }

        return {
            'product_images': product_images,
        }
