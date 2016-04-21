from django.conf.urls import include, url
from django.conf import settings
from . import views

def get_page_urls():
    """
    Put urls according to APP_BLOG_PAGE_TYPES. Example of result urls:
    'news': {'name': 'Economic news', 'alias': 'news'} --> /pages/news/3/
    'news': {'name': 'Economic news', 'alias': ''} --> /pages/3/
    """
    page_urls = []
    for page_type_id, page_type in settings.APP_BLOG_PAGE_TYPES.items():
        page_alias = page_type['alias'].strip(' /')
        pattern = '^' + page_alias + ('/' if page_alias else '') \
                      + '(?P<page_id>[0-9]+)/$'
        page_urls.append(url(pattern, views.page_item, name=page_type_id))
    return page_urls


app_name = 'blog'
urlpatterns = [
    url(r'^$', views.pages_list, name='pages_list'),
    url(r'^', include(get_page_urls())),
]
