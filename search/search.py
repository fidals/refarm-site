from functools import reduce
from typing import List, Union, Iterable
from operator import or_, add

from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models import Q, F, When, Case, Value, BooleanField
from django.shortcuts import _get_queryset


def search(term: str, model_type: Union[models.Model, models.Manager, models.QuerySet],
           lookups: list, ordering=None) -> models.QuerySet:
    """
    Return search results based on a given model
    """
    def _get_Q(lookup):
        return Q(**{lookup: term})

    term = term.strip()
    query_set = _get_queryset(model_type)
    query = reduce(or_, map(_get_Q, lookups))

    return (
        query_set.filter(query, page__is_active=True)
        .annotate(
            is_name_start_by_term=Case(When(
                name__istartswith=term, then=Value(True)), default=Value(False),
                output_field=BooleanField())
        )
        .order_by(F('is_name_start_by_term').desc(), *ordering or ('name', ))
    )


# TODO - refactor code style
def trigram_search(query: str, queryset, fields: List[str]):
    """
    Trigram similarity search. https://goo.gl/8QkFGj
    """
    query = query.strip()
    init_field, *fields = fields

    def get_trigram_similarity(field):
        return TrigramSimilarity(field, query)

    trigram_query = reduce(
        add,
        map(get_trigram_similarity, fields),
        get_trigram_similarity(init_field)
    )
    return queryset.annotate(similarity=trigram_query).order_by('-similarity')


class Search:
    def __init__(self, name, fields, qs, min_similarity=0.3, redirect_field=None):
        """
        :param name: name of model to be searched for (required only for existing interface)
        :param fields: list of query lookups
        :param qs: queryset of model to be searched for
        :param min_similarity: used to trigram similarity search
        :param redirect_field: when client search for this field, the result is 
        redirected to custom page  
        """
        self.name = name
        self.qs = qs
        self.min_similarity = min_similarity
        self.redirect_field = redirect_field

        self.fields = fields
        self.trigram_fields = []
        self.decimal_fields = []

        for field in fields:
            field_type = (
                self.qs.model._meta.get_field(field.partition('__')[0])
                    .get_internal_type()
            )
            if field_type in ['CharField', 'TextField']:
                # Trigram similarity supports only these two entity types
                self.trigram_fields.append(field)
            else:
                self.decimal_fields.append(field)

    def search(self, term: str):
        def _trigram_search(query):
            """ 
            Just a shortcut for trigram_search function call 
            """
            return trigram_search(query, self.qs, self.trigram_fields).filter(
                similarity__gt=self.min_similarity
            )

        if not term.isdecimal():
            return _trigram_search(term)

        if not self.trigram_fields:
            return search(term, self.qs, self.decimal_fields)
        elif not self.decimal_fields:
            return _trigram_search(term)
        else:
            trigram_data = _trigram_search(term)
            default_data = search(term, self.qs, self.decimal_fields)
            return trigram_data if trigram_data else default_data if default_data else None

    def search_by_redirect_field(self, term: str):
        if not self.redirect_field:
            return

        return (
            self.qs.filter(**{self.redirect_field: term}).first()
            if term.isdecimal() else None
        )


class Limit:

    def __init__(self, limit):
        self.limit = limit
        self.size = 0  # number of found elements

    def limit_data(self, data: Iterable):
        limit = self.limit - self.size
        if limit <= 0:
            return []

        limited_data = data[:limit]
        self.size += len(limited_data)

        return limited_data
