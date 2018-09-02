from refarm_pagination import Paginator, NeighborPages


class PaginationContext:

    def __init__(self, path, objects, per_page):
        self.path = path
        self.paginator = Paginator(objects, per_page)

    def context(self):
        page = self.paginator.page()
        neighbords = NeighborPages(page)

        prev_pairs = [
            (prev.number, prev.url)
            for prev in neighbords.prev_neighbors()
        ]
        next_pairs = [
            (prev.number, prev.url)
            for prev in neighbords.prev_neighbors()
        ]

        return {
            'page': page,
            'prev_pairs':prev_pairs,
            'next_pairs':next_pairs,
        }
