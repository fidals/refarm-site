import abc
import typing

from django.db.models import QuerySet


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


class ModelContext(abc.ABC):

    @abc.abstractmethod
    def qs(self) -> QuerySet:
        ...

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


Context.register(ModelContext)
