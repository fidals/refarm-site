from django import http
from django.conf import settings
from django.core import paginator


class Page(paginator.Page):

    def showed_number(self):
        return (self.number - 1) * self.paginator.per_page + len(self)



class Paginator(paginator.Paginator):

    def page(self, number) -> Page:
        """Raise Http404 instead of InvalidPage."""
        try:
            return super().page(number)
        except paginator.InvalidPage:
            raise http.Http404('Page does not exist')


class NeighborPage:

    def __init__(self, number):
        self.number = number

    def url(self, base_url):
        return base_url if self.number == 1 else f'{base_url}?page={self.number}'


class NeighborPages:

    def __init__(self, page: paginator.Page):
        self.page = page

        self._index = page.number - 1
        self._neighbor_bounds = settings.PAGINATION_NEIGHBORS // 2
        self._neighbor_range = list(self.page.paginator.page_range)

    def _neighbors(self, numbers):
        neighbors = []
        for number in numbers:
            self.page.paginator.validate_number(number)
            neighbors.append(NeighborPage(number))
        return neighbors

    def prev_neighbors(self):
        numbers = self._neighbor_range[:self._index][-self._neighbor_bounds:]
        return self._neighbors(numbers)

    def next_neighbors(self):
        numbers = self._neighbor_range[self._index + 1:][:self._neighbor_bounds]
        return self._neighbors(numbers)
