from django.conf import settings
from django.core import paginator
from django.test import TestCase
from django.http import Http404

from refarm_pagination import pagination


class Paginator(TestCase):

    def test_page_404error(self):
        with self.assertRaises(Http404):
            pagination.Paginator([], 1).page(2)

    def test_page_result(self):
        self.assertIsInstance(
            pagination.Paginator([], 1).page(1),
            paginator.Page,
        )


class NeighborPage(TestCase):

    def test_first_page_url(self):
        """First page gives url without `page` query string param."""
        base_url = 'url'
        self.assertEqual(
            base_url,
            pagination.NeighborPage(1).url(base_url),
        )

    def test_rest_page_urls(self):
        """Any page gives url with `page` query string param exept the first page."""
        page_number = 2
        base_url = 'url'
        self.assertEqual(
            f'{base_url}?page={page_number}',
            pagination.NeighborPage(page_number).url(base_url),
        )


class NeighborPages(TestCase):

    def neighbors(self, object_count, per_page, page_number):
        return pagination.NeighborPages(
            pagination.Paginator(
                list(range(object_count)),
                per_page,
            ).page(page_number),
        )

    def test_neighbors(self):
        """The current page is not in the list of neighbors."""
        page_number = 3
        neighbors = self.neighbors(object_count=10, per_page=2, page_number=page_number)

        for neighbor in neighbors.prev_neighbors() + neighbors.next_neighbors():
            self.assertNotEqual(neighbor.number, page_number)

    def test_neighbor_count(self):
        page_number = 3
        neighbors = self.neighbors(object_count=10, per_page=2, page_number=page_number)

        self.assertEqual(
            settings.PAGINATION_NEIGHBORS,
            len(neighbors.prev_neighbors() + neighbors.next_neighbors()),
        )
