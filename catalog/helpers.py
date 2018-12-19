from urllib.parse import urlencode

from django.urls import reverse

from catalog.models import AbstractCategory, TagQuerySet


def reverse_catalog_url(
    url: str,
    route_kwargs: dict,
    tags: TagQuerySet=None,
    sorting: int=None,
    query_string: dict=None,
) -> str:
    query_string = f'?{urlencode(query_string)}' if query_string else ''
    if tags:
        # PyCharm's option:
        # noinspection PyTypeChecker
        tags_slug = tags.as_url()
        route_kwargs['tags'] = tags_slug
    if sorting is not None:
        route_kwargs['sorting'] = sorting

    return f'{reverse(url, kwargs=route_kwargs)}{query_string}'
