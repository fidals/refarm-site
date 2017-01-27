from catalog.views import search, catalog
from tests.catalog.models import TestCategory, TestProduct


class TestCategoryTree(catalog.CategoryTree):
    category_model = TestCategory


class TestSearch(search.Search):
    model_map = {'category': TestCategory, 'product': TestProduct}


class TestProductPage(catalog.ProductPage):
    """Product page view."""
    model = TestProduct


class TestProductsWithoutImages(catalog.ProductsWithoutImages):
    model = TestProduct


class TestProductsWithoutText(catalog.ProductsWithoutImages):
    model = TestProduct
