import abc
import collections
import typing


class Context(abc.ABC):

    @abc.abstractmethod
    def context(self) -> typing.Dict[str, typing.Any]:
        ...


class Contexts(Context):

    def __init__(self, *contexts: typing.List[Context]):
        self.contexts = contexts

    def context(self):
        return dict(collections.ChainMap(
            *[ctx.context() for ctx in self.contexts]
        ))
