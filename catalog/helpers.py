from urllib.parse import urlencode

from django.urls import reverse

from catalog.models import AbstractCategory, TagQuerySet


def get_category_path(
    category: AbstractCategory,
    route_name='category',
    tags: TagQuerySet=None,
    sorting: int=None,
    query_string: dict=None,
):
    query_string = f'?{urlencode(query_string)}' if query_string else ''
    route_kwargs = {
        'category_id': category.id,
        **({'tags': tags.as_url()} if tags else {}),
        **({'sorting': sorting} if sorting is not None else {}),
    }

    return f'{reverse(route_name, kwargs=route_kwargs)}{query_string}'
