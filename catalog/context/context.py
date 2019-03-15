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
