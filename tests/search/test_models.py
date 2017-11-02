from functools import partial

from django.test import TestCase

from search.search import search
from tests.catalog.models import MockCategory, MockProduct


class TestSearch(TestCase):
    """Test suite for catalog model's search"""

    lookups = ['name__icontains', 'id__contains']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.batteries_category = MockCategory.objects.create(
            name='Batteries'
        )

        # first product in search results
        cls.results_first_product = MockProduct.objects.create(
            name='Battery Т-34',
            price=20,
            category=cls.batteries_category,
            in_stock=10,
            is_popular=True,
        )

        # second product in search results
        cls.results_second_product = MockProduct.objects.create(
            name='Cool battery for deers',
            price=20,
            category=cls.batteries_category,
            in_stock=10,
            is_popular=True,
        )

        cls.search = partial(search, model_type=MockProduct, lookups=cls.lookups)

    def test_results_order_is_right(self):
        """Search results order should be right"""
        term = 'Battery'

        products = iter(self.search(term))

        self.assertEqual(next(products).name, self.results_first_product.name)
        self.assertEqual(next(products).name, self.results_second_product.name)

    def test_wrong_term_leads_to_empty_results(self):
        """Search results for wrong term should be empty"""
        term = 'Wrong query <some hash here>'

        products = self.search(term)

        self.assertFalse(products)

    def test_unique_term_leads_to_single_result(self):
        """Unique search term leads to single result"""
        term = 'Battery Т-34'

        products = self.search(term)

        self.assertEqual(len(products), 1)

    def test_middle_term_inclusion_is_searchable(self):
        """
        User can search by term even
        term is at the middle of the items name
        """
        term = 'for deer'

        products = iter(self.search(term))

        self.assertEqual(next(products).name, self.results_second_product.name)
