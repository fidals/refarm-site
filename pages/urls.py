from typing import List
from django.conf.urls import include, url
from django.conf import settings

from . import views


def get_post_urls() -> List[str]:
    """
    Return urls created according to APP_BLOG_POST_TYPES.
    Example of result urls:
     'news': {'name': 'Economic news', 'slug': 'news'} --> /pages/news/3/
     'news': {'name': 'Economic news', 'slug': ''} --> /pages/3/
    """

    def _get_pattern(post_type_slug: str) -> str:
        """Returns post's url pattern by given post type slug"""
        slug = post_type_slug.strip(' /')
        slug = (slug + '/') if slug else ''
        return '^{0}(?P<slug_>[\w-]+)/$'.format(slug)

    def _get_url(post_type_id, post_type_slug):
        return url(
            _get_pattern(post_type_slug),
            views.post_item,
            name=post_type_id,
            kwargs={'type_': post_type_id}
        )

    return [_get_url(id_, type_['alias'])
            for id_, type_ in settings.APP_BLOG_POST_TYPES.items()]


app_name = 'pages'
urlpatterns = [
    url(r'^$', views.post_types, name='post_types'),
    url(r'^posts/(?P<type_>[\w-]+)/$', views.posts, name='posts'),
    url(r'^', include(get_post_urls())),
]
