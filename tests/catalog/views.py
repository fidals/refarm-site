from catalog.views import catalog
from tests.catalog.models import TestCategory, TestProduct


class TestCategoryTree(catalog.CategoryTree):
    category_model = TestCategory


class TestProductPage(catalog.ProductPage):
    """Product page view."""
    model = TestProduct


class TestProductsWithoutImages(catalog.ProductsWithoutImages):
    model = TestProduct


class TestProductsWithoutText(catalog.ProductsWithoutImages):
    model = TestProduct
