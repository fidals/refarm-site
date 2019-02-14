import abc
import collections

from catalog import typing


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


class ModelContext(abc.ABC):

    def __init__(self, qs: typing.QuerySet):
        self._qs = qs

    def qs(self):
        return self._qs

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


Context.register(ModelContext)


class Contexts(Context):

    # use context as list, not as args pack (`*context`)
    # to move attention on homogeneous nature of args
    def __init__(self, contexts: typing.List[Context]):
        self.contexts = contexts or []

    def context(self):
        return dict(collections.ChainMap(
            *[ctx.context() for ctx in self.contexts]
        ))


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
