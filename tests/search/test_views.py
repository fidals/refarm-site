import json

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest import expectedFailure

from pages.models import CustomPage

from tests.catalog.models import MockCategory, MockProduct


def json_as_dict(response: HttpResponse) -> dict:
    return json.loads(response.content.decode())


@override_settings(ROOT_URLCONF='tests.urls')
class AbstractTestSearchView(TestCase):

    fixtures = ['catalog.json']

    def setUp(self):
        """Instantiate two test objects: test_category and test_product"""
        self.test_products = MockProduct.objects.all()
        self.search_page = CustomPage.objects.get(slug='search')


class TestSearchView(AbstractTestSearchView):

    def get_search_results(self, term: str):
        url = f'{self.search_page.url}?term={term}'
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Search page based on unique term should contain single result"""
        product = self.test_products.first()
        term = ' '.join(product.name.split(' ')[:2])
        response = self.get_search_results(term)
        self.assertContains(response, product.name)

    def test_search_empty_result_by_wrong_term(self):
        """Search page based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_search_results(term)
        self.assertNotContains(response, 'class="search-result-item"')
        self.assertContains(response, 'Nothing was found on your request')

    def test_search_results_order(self):
        """
        @todo #85 - Fix search results order
         Search results with leading term in result text
         should go before other results
        """
        first, second = self.test_products.filter(name__icontains='Battery')[:2]
        response = self.get_search_results(first.name)
        first_position = str(response.content).find(first.name)
        second_position = str(response.content).find(second.name)
        self.assertGreater(second_position, first_position)


class TestAutocompleteView(AbstractTestSearchView):

    def get_autocomplete_results(self, term: str, page_type: str):
        url = f'{reverse("mock_autocomplete")}?term={term}&pageType={page_type}'
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Autocomplete content based on unique term should contain single result"""
        product_name = self.test_products.first().name
        term = product_name.split(' ')[-1]
        response = self.get_autocomplete_results(product_name, 'product')
        self.assertContains(response, product_name)

    def test_search_empty_result_by_wrong_term(self):
        """Autocomplete content based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_autocomplete_results(term, 'product')
        self.assertFalse(json_as_dict(response))


class TestAdminAutocompleteView(AbstractTestSearchView):

    def get_admin_autocomplete_results(self, term: str, page_type: str):
        url = f'{reverse("mock_admin_autocomplete")}?term={term}&pageType={page_type}'
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Autocomplete content based on unique term should contain single result"""
        product_name = self.test_products.first().name
        term = product_name.split(' ')[-1]
        response = self.get_admin_autocomplete_results(term, 'product')
        self.assertContains(response, product_name)

    def test_search_empty_result_by_wrong_term(self):
        """Autocomplete content based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_admin_autocomplete_results(term, 'product')
        self.assertFalse(json_as_dict(response))
