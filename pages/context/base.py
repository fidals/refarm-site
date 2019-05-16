import abc
import collections

from pages import typing


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.ContextDict:
        ...


class Contexts(Context):

    # use context as list, not as args pack (`*context`)
    # to move attention on homogeneous nature of args
    def __init__(self, contexts: typing.List[Context]):
        self.contexts = contexts or []

    def context(self) -> typing.ContextDict:
        return dict(collections.ChainMap(
            *[ctx.context() for ctx in self.contexts]
        ))
