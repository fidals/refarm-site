from catalog.views import catalog
from tests.catalog.models import MockCategory, MockProduct


class TestCategoryTree(catalog.CategoryTree):
    category_model = MockCategory


class TestProductPage(catalog.ProductPage):
    """Product page view."""
    model = MockProduct


class TestProductsWithoutImages(catalog.ProductsWithoutImages):
    model = MockProduct


class TestProductsWithoutText(catalog.ProductsWithoutImages):
    model = MockProduct
