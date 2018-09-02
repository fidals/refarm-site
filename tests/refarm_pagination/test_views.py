from contextlib import contextmanager
from unittest import mock

from django.conf import settings
from django.test import TestCase
from refarm_pagination import views, pagination

from tests.catalog.models import MockProduct


class PaginationContext(TestCase):

    fixtures = ['catalog.json']

    def context(self, **kwargs):
        return views.PaginationContext(**{
            'url': '',
            'number': 3,
            'per_page': 3,
            'objects': MockProduct.objects.all(),
            **kwargs
        }).context()

    @contextmanager
    def mock_neighbor_pairs(self, url, number):
        with \
            mock.patch('refarm_pagination.pagination.NeighborPage') as mocked_page,\
            mock.patch('refarm_pagination.pagination.NeighborPages') as mocked_pages:

            pages = mocked_pages.return_value
            mocked_page.return_value.url = lambda _: url
            mocked_page.return_value.number = number

            pages.next_neighbors = pages.prev_neighbors = lambda: [mocked_page] * 2

            yield mocked_page, mocked_pages

    def test_page_number(self):
        with mock.patch('django.core.paginator.Page') as mocked:
            number = mocked.return_value.number = 1
            self.assertEquals(
                self.context()['page'].number,
                number
            )

    def test_neighbor_pairs_content(self):
        url = 'url'
        number = 1

        with self.mock_neighbor_pairs(url, number):
            context = self.context()
            for index, key_name in zip([-1, 0], ['prev_pairs', 'next_pairs']):
                self.assertEquals(
                    (number, url),
                    context[key_name][index]
                )

    def test_showed_number(self):
        per_page = number = 3

        self.assertEquals(
            self.context(per_page=per_page, number=number)['showed_number'],
            number * per_page,
        )
