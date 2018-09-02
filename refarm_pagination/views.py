from django.conf import settings
from django.core.paginator import Paginator, InvalidPage


class PaginatorLinks:

    def __init__(self, number, path, paginated: Paginator):
        self.paginated = paginated
        self.number = number
        self.path = path

        self.index = number - 1
        self.neighbor_bounds = settings.PAGINATION_NEIGHBORS // 2
        self.neighbor_range = list(self.paginated.page_range)

    def page(self):
        try:
            return self.paginated.page(self.number)
        except InvalidPage:
            raise http.Http404('Page does not exist')

    def showed_number(self):
        return self.index * self.paginated.per_page + self.page().object_list.count()

    def _url(self, number):
        self.paginated.validate_number(number)
        return self.path if number == 1 else f'{self.path}?page={number}'

    def prev_numbers(self):
        return self.neighbor_range[:self.index][-self.neighbor_bounds:]

    def next_numbers(self):
        return self.neighbor_range[self.index + 1:][:self.neighbor_bounds]

    def number_url_map(self):
        numbers = self.prev_numbers() + self.next_numbers()
        return {number: self._url(number) for number in numbers}
