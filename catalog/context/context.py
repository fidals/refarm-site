import abc
import typing

from django.db.models import QuerySet


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> Dict[str, typing.Any]:
        ...


class ModelContext(abc.ABC, Context):

    @abc.abstractmethod
    def qs(self) -> QuerySet:
        ...

