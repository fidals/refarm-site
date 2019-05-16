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
from itertools import chain

from django.db.models import QuerySet
from django.http import JsonResponse

from images.models import Image
from pages import typing


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


class Results:
    def __init__(self, results_qs: QuerySet):
        """`results_qs` is QuerySet with already searched and sorted entities."""
        isinstance(results_qs.model, Representable)
        self.qs = results_qs

    def list(self) -> typing.List[Result]:
        return [Result(o) for o in self.qs]


class ResultsStack:
    """Merge results by different strategies."""

    def __init__(self, result_sets: typing.Iterable[Results]):
        self.sets = result_sets

    def chain(self) -> typing.Iterator[Result]:
        return chain(*self.sets)


# it's some client code:
class CategoryQuerySet(QuerySet):
    pass


class ProductQuerySet(QuerySet):
    pass


def autocomplete(request, query):
    # we'll use django orm search based on postgresql.
    # Query sets will already contain searched entities.
    return JsonResponse(list(
        ResultsStack([
            Results(
                CategoryQuerySet().filter(name__search=query),
            ),
            Results(
                ProductQuerySet().filter(name__search=query),
            ),
        ]).chain()
    ))
