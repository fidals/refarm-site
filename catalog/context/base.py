import abc

from catalog import typing
from pages.context import Context


class ModelContext(abc.ABC):

    def __init__(self, qs: typing.QuerySet):
        self._qs = qs

    def qs(self):
        return self._qs

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


Context.register(ModelContext)


class Tags(ModelContext):

    def context(self):
        return {
            'tags': self.qs(),
        }


class Products(Context):

    def __init__(self, products: typing.ProductQuerySet):
        self._products = products

    @property
    def products(self):
        return self._products

    def context(self):
        return {
            'products': self.products,
        }


class Page(Context):

    def __init__(self, page, tags: Tags):
        self._page = page
        self._tags = tags

    def context(self) -> typing.ContextDict:
        tags_qs = self._tags.qs()
        # use dirty patch here, because it's the most simple method
        # to make shared templates work.
        # For example `templates/layout/metadata.html`.
        self._page.display = {
            'page': self._page,
            'tag_titles': tags_qs.as_title(),
            'tags': tags_qs,
        }
        return {
            'page': self._page,
        }
