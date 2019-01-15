import abc
import collections
import typing

from django.db.models import QuerySet


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


class ModelContext(abc.ABC):

    def __init__(self, qs: QuerySet):
        self._qs = qs

    def qs(self):
        return self._qs

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


Context.register(ModelContext)


class Contexts(Context):

    def __init__(self, *contexts: typing.List[Context]):
        self.contexts = contexts

    def context(self):
        return dict(collections.ChainMap(
            *[ctx.context() for ctx in self.contexts]
        ))


class Tags(ModelContext):

    def context(self):
        return {
            'tags': self.qs(),
        }


class Products(ModelContext):

    def context(self):
        return {
            'products': self.qs(),
        }
