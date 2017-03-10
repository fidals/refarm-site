from typing import List
from functools import reduce

from django.conf import settings
from django.contrib.postgres import search
from django.db import models


class SearchQuerySet(models.QuerySet):

    def search(self, query: str, fields: List):
        query = query.strip()

    def trigram_search(self, query: str, fields: List):
        """
        Trigram similarity search. https://goo.gl/8QkFGj

        >>> qs = Model.objects.annotate(tg_search=TrigramSimilarity('field_name', 'que'))
        >>> qs.filter(tg_search__gt=0.3)
        <QuerySet [<Model: uefa>], [<Model: query>], [<Model: que>], [<Model: queryset>]>
        """
        query = query.strip()
        init_field, *fields = fields

        def get_trigram(field):
            return search.TrigramSimilarity(field, query)

        def get_trigram_query(x, y):
                return x + get_trigram(y)

        similarity = reduce(get_trigram_query, fields, initial=get_trigram(init_field))
        return self.aggregate(similarity=similarity).order_by('-similarity')
