from refarm_pagination.pagination import Paginator, NeighborPages


class PaginationContext:

    def __init__(self, url, number, per_page, objects):
        self.url = url
        self.number = number
        self.paginator = Paginator(objects, per_page)

    def context(self):
        page = self.paginator.page(self.number)
        showed_number = (self.number - 1) * self.paginator.per_page + len(page)
        neighbords = NeighborPages(page)

        prev_pairs = [
            (prev.number, prev.url(self.url))
            for prev in neighbords.prev_neighbors()
        ]
        next_pairs = [
            (prev.number, prev.url(self.url))
            for prev in neighbords.next_neighbors()
        ]

        return {
            'page': page,
            'prev_pairs':prev_pairs,
            'next_pairs':next_pairs,
            'showed_number': showed_number,
        }
