"""
This is temporary module with the arch concept for the search.

@todo #331:60m  Implement the new arch at the search app.
 All you need is to implement ContextsStack class
 and place the other classes to the relevant places.
 `search.search` module will be fully rewritten.
 You also can drop away starting_by_term functionality.
 See "is_name_start_by_term" aggregation parameter
 inside search.search.search function.
"""

import abc

from django.db.models import QuerySet
from django.http import JsonResponse

from images.models import Image
from pages import typing
from pages.context import Context


class Representable(abc.ABC):
    @property
    def name(self):
        raise NotImplemented()

    @property
    def url(self):
        raise NotImplemented()


class Result:
    def __init__(self, item: Representable):
        self.name: str = item.name
        self.url: str = item.url
        self.image: Image = getattr(item, 'image', None)
        self.price: float = getattr(item, 'price', 0.0)


class ResultsContext(Context):
    def __init__(self, results_qs: QuerySet):
        """`results_qs` is QuerySet with already searched and sorted entities."""
        isinstance(results_qs.model, Representable)
        self.qs = results_qs

    def context(self):
        return {
            'results': [Result(o) for o in self.qs],
        }


class ContextsStack:
    """Merge context dicts by different strategies."""

    def __init__(self, contexts: typing.Iterable[Context]):
        self.contexts = list(contexts)

    def any(self) -> typing.ContextDict:
        """Stack contexts with with disjunction principle."""
        raise NotImplemented()

    # don't implement it. Just for arch design demonstration
    def all(self):
        ...


# it's some client code:
class CategoryQuerySet(QuerySet):
    pass


class ProductQuerySet(QuerySet):
    pass


def autocomplete(request, query):
    return JsonResponse(
        # we'll use django orm search based on postgresql.
        # Query sets will already contain searched entities.
        ContextsStack([
            ResultsContext(
                CategoryQuerySet().filter(name__search=query),
            ),
            ResultsContext(
                ProductQuerySet().filter(name__search=query),
            ),
        ]).any()
    )
