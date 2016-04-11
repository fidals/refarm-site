from django.conf.urls import include, url
from django.conf import settings
from . import views


def get_pattern(alias):
    alias = alias.strip(' /')
    return '^' + alias + ('/' if alias else '') + '(?P<post_id>[0-9]+)/$'


def get_post_urls():
    """
    Return urls created according to APP_BLOG_POST_TYPES.
    Example of result urls:
     'news': {'name': 'Economic news', 'alias': 'news'} --> /pages/news/3/
     'news': {'name': 'Economic news', 'alias': ''} --> /pages/3/
    """
    return [url(
        get_pattern(post_type['alias']),
        views.post_item,
        name=post_type_id
    ) for post_type_id, post_type in settings.APP_BLOG_POST_TYPES.items()]


app_name = 'blog'
urlpatterns = [
    url(r'^$', views.posts_list, name='posts_list'),
    url(r'^', include(get_post_urls())),
]
