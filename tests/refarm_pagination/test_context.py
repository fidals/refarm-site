from contextlib import contextmanager
from unittest import mock

from django.conf import settings
from django.test import TestCase
from refarm_pagination.context import PaginationContext

from tests.catalog.models import MockProduct


class TestPaginationContext(TestCase):

    fixtures = ['catalog.json']

    def context(self, **kwargs):
        return PaginationContext(**{
            'url': '',
            'number': 1,
            'per_page': 1,
            'objects': MockProduct.objects.all(),
            **kwargs
        }).context()

    @contextmanager
    def mock_neighbor_pairs(self, url, number):
        with mock.patch('refarm_pagination.context.NeighborPages') as mocked_pages:
            mocked_page = mock.Mock()
            mocked_page.url = lambda _: url
            mocked_page.number = number

            get_neighbors = lambda: [mocked_page] * (settings.PAGINATION_NEIGHBORS // 2)
            pages = mocked_pages.return_value
            pages.next_neighbors = pages.prev_neighbors = get_neighbors

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

    def test_showed_count(self):
        per_page = number = 3

        self.assertEquals(
            self.context(per_page=per_page, number=number)['showed_count'],
            number * per_page,
        )
