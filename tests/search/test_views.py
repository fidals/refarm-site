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

    # @todo #85 Create fixtures for tests
    #  now we have huge code doubling

    @classmethod
    def setUpTestData(cls):
        """Instantiate two test objects: test_category and test_product"""
        cls.search, _ = CustomPage.objects.get_or_create(slug='search')

        def generate_products(cls):
            return [
                MockProduct.objects.create(
                    name=name,
                    category=cls.test_category,
                ) for name in cls.test_products
            ]

        cls.test_category = MockCategory.objects.create(
            name='Batteries for deers',
        )
        cls.test_category.slug = ''
        cls.test_category.page.position = 1
        cls.test_category.page.save()
        cls.test_products = [
            'Battery from Fenich',
            'Battery from Djalal',
            'Box for battery',
        ]
        generate_products(cls)


class TestSearchView(AbstractTestSearchView):
    def get_search_results(self, term: str):
        url = f'{self.search.url}?term={term}'
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Search page based on unique term should contain single result"""
        term = 'fenich'
        response = self.get_search_results(term)
        self.assertContains(response, self.test_products[0])

    def test_search_empty_result_by_wrong_term(self):
        """Search page based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_search_results(term)
        self.assertNotContains(response, 'class="search-results-item"')
        self.assertContains(response, 'Nothing was found on your request')

    @expectedFailure
    def test_search_results_order(self):
        """
        @todo #85 - Fix search results order
         Search results with leading term in result text
         should go before other results
        """
        response = self.get_search_results('battery')
        first_position = str(response.content).find(self.test_products[0])
        second_position = str(response.content).find(self.test_products[2])
        self.assertGreater(second_position, first_position)


class TestAutocompleteView(AbstractTestSearchView):
    def get_autocomplete_results(self, term: str):
        url = reverse('mock_autocomplete') + f'?term={term}'
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Autocomplete content based on unique term should contain single result"""
        term = 'fenich'
        response = self.get_autocomplete_results(term)
        self.assertContains(response, self.test_products[0])

    def test_search_empty_result_by_wrong_term(self):
        """Autocomplete content based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_autocomplete_results(term)
        self.assertFalse(json_as_dict(response))


class TestAdminAutocompleteView(AbstractTestSearchView):
    def get_admin_autocomplete_results(self, term: str, page_type: str):
        url = (
            reverse('mock_admin_autocomplete')
            + f'?term={term}&pageType={page_type}'
        )
        # `follow=True` is required for 301 urls
        return self.client.get(url, follow=True)

    def test_search_single_result_by_unique_term(self):
        """Autocomplete content based on unique term should contain single result"""
        term = 'fenich'
        response = self.get_admin_autocomplete_results(term, 'product')
        self.assertContains(response, self.test_products[0])

    def test_search_empty_result_by_wrong_term(self):
        """Autocomplete content based on wrong term should contain no results"""
        term = 'fenich_is_god_of_business'
        response = self.get_admin_autocomplete_results(term, 'product')
        self.assertFalse(json_as_dict(response))
