from .base import Context


class Page(Context):

    def __init__(self, page):
        self.page = page

    def context(self):
        return {
            'page': self.page,
        }
