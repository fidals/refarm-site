import abc
import collections
import typing


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


class Contexts(Context):

    # use context as list, not as args pack (`*context`)
    # to move attention on homogeneous nature of args
    def __init__(self, contexts: typing.List[Context]):
        self.contexts = contexts or []

    def context(self):
        return dict(collections.ChainMap(
            *[ctx.context() for ctx in self.contexts]
        ))


class SimpleContext(Context):
    """Context object constructed from given context dict."""

    def __init__(self, context: dict):
        self._context = context

    # TODO - rm it
    @property
    def products(self):
        return self._context['products']

    def context(self):
        return self._context
